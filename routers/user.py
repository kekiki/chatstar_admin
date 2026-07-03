from fastapi import APIRouter, Request, Depends, Query, Body
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_, cast, String
from database import get_db
from tools import get_page_params, paginate_query
import models
import datetime

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
    db: Session = Depends(get_db),
    page: int = Query(1),
    page_size: int = Query(10),
    keyword: str = Query("", description="全字段模糊搜索"),
    start_date: str = Query(""),
    end_date: str = Query(""),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    apps = db.query(models.AppList).all()
    page, page_size, offset = get_page_params(page, page_size)
    q = db.query(models.AppUser)

    if keyword:
        q = q.filter(
            or_(
                cast(models.AppUser.user_id, String).like(f"%{keyword}%"),
                models.AppUser.device_id.like(f"%{keyword}%"),
                cast(models.AppUser.app_id, String).like(f"%{keyword}%"),
                models.AppUser.nickname.like(f"%{keyword}%"),
                models.AppUser.email.like(f"%{keyword}%"),
                models.AppUser.google_id.like(f"%{keyword}%")
            )
        )

    page_data = paginate_query(db, q, offset, page_size)
    return templates.TemplateResponse(request, "user_list.html", {
        "request": request,
        "active_menu": "user",
        "apps": apps,
        "page_data": page_data,
        "keyword": keyword,
        "start_date": start_date,
        "end_date": end_date
    })

@router.put("/admin/api/update_user")
async def update_user(
    request: Request,
    user_id: int = Body(...),
    avatar: str = Body(""),
    nickname: str = Body(""),
    country: str = Body(""),
    balance: int = Body(0),
    is_vip: bool = Body(False),
    is_check: bool = Body(False),
    db: Session = Depends(get_db),
    _user = Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    user = db.query(models.AppUser).filter(models.AppUser.user_id == user_id).first()
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
    if is_vip is not None:
        user.is_vip = is_vip
    if is_check is not None:
        user.is_check = is_check
    
    db.commit()
    db.refresh(user)
    return {
        "code": 200,
        "msg": "更新成功",
        "user": {
            "user_id": user.user_id,
            "avatar": user.avatar,
            "nickname": user.nickname,
            "country": user.country,
            "balance": user.balance,
            "is_vip": user.is_vip,
            "is_check": user.is_check,
        }
    }
