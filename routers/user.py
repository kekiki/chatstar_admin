from fastapi import APIRouter, Request, Depends, Query, Body
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, or_, cast, String
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from tools import get_page_params, paginate_query
import models
import datetime
from typing import Optional, Union

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Add datetime filter to Jinja2 environment
def datetime_format(timestamp):
    if not timestamp:
        return ""
    try:
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return str(timestamp)

templates.env.filters["datetime_format"] = datetime_format

@router.get("/admin/user", response_class=HTMLResponse)
async def user_list(
    request: Request,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1),
    page_size: int = Query(10),
    keyword: str = Query("", description="全字段模糊搜索"),
    start_date: str = Query(""),
    end_date: str = Query(""),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    apps_stmt = select(models.AppList)
    apps_result = await db.execute(apps_stmt)
    apps = apps_result.scalars().all()
    page, page_size, offset = get_page_params(page, page_size)
    q = select(models.AppUser)

    if keyword:
        q = q.where(
            or_(
                cast(models.AppUser.user_id, String).like(f"%{keyword}%"),
                models.AppUser.device_id.like(f"%{keyword}%"),
                models.AppUser.package_name.like(f"%{keyword}%"),
                models.AppUser.nickname.like(f"%{keyword}%"),
                models.AppUser.email.like(f"%{keyword}%"),
                models.AppUser.google_id.like(f"%{keyword}%")
            )
        )

    page_data = await paginate_query(db, q, offset, page_size)

    # Fetch black/white status data
    user_ids = [user.user_id for user in page_data["list"]]
    device_ids = [user.device_id for user in page_data["list"] if user.device_id]
    ips = [user.ip for user in page_data["list"] if user.ip]

    # Fetch account status
    account_status_map = {}
    if user_ids:
        bw_user_stmt = select(models.BlackWhiteUser).where(models.BlackWhiteUser.user_id.in_(user_ids))
        bw_user_result = await db.execute(bw_user_stmt)
        bw_users = bw_user_result.scalars().all()
        for bw_user in bw_users:
            account_status_map[bw_user.user_id] = bw_user.status

    # Fetch device status
    device_status_map = {}
    if device_ids:
        bw_device_stmt = select(models.BlackWhiteDevice).where(models.BlackWhiteDevice.device_id.in_(device_ids))
        bw_device_result = await db.execute(bw_device_stmt)
        bw_devices = bw_device_result.scalars().all()
        for bw_device in bw_devices:
            device_status_map[bw_device.device_id] = bw_device.status

    # Fetch IP status
    ip_status_map = {}
    if ips:
        bw_ip_stmt = select(models.BlackWhiteIp).where(models.BlackWhiteIp.ip.in_(ips))
        bw_ip_result = await db.execute(bw_ip_stmt)
        bw_ips = bw_ip_result.scalars().all()
        for bw_ip in bw_ips:
            ip_status_map[bw_ip.ip] = bw_ip.status

    # Add status info to each user
    for user in page_data["list"]:
        user.account_status = account_status_map.get(user.user_id, None)  # None means normal
        user.device_status = device_status_map.get(user.device_id, None) if user.device_id else None
        user.ip_status = ip_status_map.get(user.ip, None) if user.ip else None

    return templates.TemplateResponse(request, "user_list.html", {
        "request": request,
        "active_menu": "user",
        "apps": apps,
        "page_data": page_data,
        "keyword": keyword,
        "start_date": start_date,
        "end_date": end_date,
        "current_timestamp": int(datetime.datetime.now().timestamp())
    })

@router.put("/admin/api/update_user")
async def update_user(
    request: Request,
    user_id: int = Body(...),
    avatar: str = Body(""),
    nickname: str = Body(""),
    country: str = Body(""),
    balance: int = Body(0),
    vip_expire_time: int = Body(None),
    is_review: bool = Body(False),
    account_status: Optional[Union[int, str]] = Body(None),
    ip_status: Optional[Union[int, str]] = Body(None),
    device_status: Optional[Union[int, str]] = Body(None),
    db: AsyncSession = Depends(get_db),
    _user = Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    stmt = select(models.AppUser).where(models.AppUser.user_id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        return {"code": 404, "msg": "用户不存在"}

    if avatar is not None:
        user.avatar = avatar
    if nickname is not None:
        user.nickname = nickname
    if country is not None:
        user.country = country
    if balance is not None:
        user.balance = balance
    if vip_expire_time is not None:
        user.vip_expire_time = vip_expire_time
    if is_review is not None:
        user.is_review = is_review

    # Handle account status
    def parse_status(value):
        if value == "":
            return ""
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return value

    account_status = parse_status(account_status)
    ip_status = parse_status(ip_status)
    device_status = parse_status(device_status)

    if account_status is not None:
        if account_status == "":
            # Remove from black/white list
            bw_user_stmt = select(models.BlackWhiteUser).where(models.BlackWhiteUser.user_id == user_id)
            bw_user_result = await db.execute(bw_user_stmt)
            bw_user = bw_user_result.scalar_one_or_none()
            if bw_user:
                await db.delete(bw_user)
        else:
            # Update or insert
            bw_user_stmt = select(models.BlackWhiteUser).where(models.BlackWhiteUser.user_id == user_id)
            bw_user_result = await db.execute(bw_user_stmt)
            bw_user = bw_user_result.scalar_one_or_none()
            if bw_user:
                bw_user.status = account_status
            else:
                bw_user = models.BlackWhiteUser(user_id=user_id, status=account_status)
                db.add(bw_user)

    # Handle IP status
    if ip_status is not None and user.ip:
        if ip_status == "":
            # Remove from black/white list
            bw_ip_stmt = select(models.BlackWhiteIp).where(models.BlackWhiteIp.ip == user.ip)
            bw_ip_result = await db.execute(bw_ip_stmt)
            bw_ip = bw_ip_result.scalar_one_or_none()
            if bw_ip:
                await db.delete(bw_ip)
        else:
            # Update or insert
            bw_ip_stmt = select(models.BlackWhiteIp).where(models.BlackWhiteIp.ip == user.ip)
            bw_ip_result = await db.execute(bw_ip_stmt)
            bw_ip = bw_ip_result.scalar_one_or_none()
            if bw_ip:
                bw_ip.status = ip_status
            else:
                bw_ip = models.BlackWhiteIp(ip=user.ip, status=ip_status)
                db.add(bw_ip)

    # Handle device status
    if device_status is not None and user.device_id:
        if device_status == "":
            # Remove from black/white list
            bw_device_stmt = select(models.BlackWhiteDevice).where(models.BlackWhiteDevice.device_id == user.device_id)
            bw_device_result = await db.execute(bw_device_stmt)
            bw_device = bw_device_result.scalar_one_or_none()
            if bw_device:
                await db.delete(bw_device)
        else:
            # Update or insert
            bw_device_stmt = select(models.BlackWhiteDevice).where(models.BlackWhiteDevice.device_id == user.device_id)
            bw_device_result = await db.execute(bw_device_stmt)
            bw_device = bw_device_result.scalar_one_or_none()
            if bw_device:
                bw_device.status = device_status
            else:
                bw_device = models.BlackWhiteDevice(device_id=user.device_id, status=device_status)
                db.add(bw_device)

    await db.commit()
    await db.refresh(user)
    return {
        "code": 200,
        "msg": "更新成功",
        "user": {
            "user_id": user.user_id,
            "avatar": user.avatar,
            "nickname": user.nickname,
            "country": user.country,
            "balance": user.balance,
            "vip_expire_time": user.vip_expire_time,
            "is_review": user.is_review,
        }
    }

@router.put("/admin/api/change_password")
async def change_password(
    request: Request,
    user_id: int = Body(...),
    new_password: str = Body(...),
    db: AsyncSession = Depends(get_db),
    _user = Depends(lambda: None)
):
    from routers.auth import require_login
    import hashlib
    _user = require_login(request, db)
    stmt = select(models.AppUser).where(models.AppUser.user_id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        return {"code": 404, "msg": "用户不存在"}

    # Hash the password (using MD5 as it seems to be the existing method)
    user.password = hashlib.md5(new_password.encode()).hexdigest()

    await db.commit()
    await db.refresh(user)
    return {
        "code": 200,
        "msg": "密码修改成功"
    }
