from fastapi import APIRouter, Request, Depends, Query, Body, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, or_, cast, String
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from tools import get_page_params, paginate_query
import models
import random
import datetime
from r2_client import R2Client
from image_utils import compress_image

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def datetime_format(timestamp):
    if not timestamp:
        return ""
    try:
        dt = datetime.datetime.fromtimestamp(int(timestamp))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(timestamp)

templates.env.filters["datetime_format"] = datetime_format

@router.get("/admin/anchor", response_class=HTMLResponse)
async def anchor_list(
    request: Request,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1),
    page_size: int = Query(10),
    keyword: str = Query("", description="全字段模糊搜索"),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    page, page_size, offset = get_page_params(page, page_size)
    q = select(models.AppUser).where(models.AppUser.is_anchor == True).order_by(models.AppUser.created_time.desc())

    if keyword:
        q = q.where(
            or_(
                cast(models.AppUser.user_id, String).like(f"%{keyword}%"),
                models.AppUser.nickname.like(f"%{keyword}%"),
                models.AppUser.country.like(f"%{keyword}%"),
                models.AppUser.language_name.like(f"%{keyword}%"),
                models.AppUser.language_code.like(f"%{keyword}%")
            )
        )

    page_data = await paginate_query(db, q, offset, page_size)
    return templates.TemplateResponse(request, "anchor_list.html", {
        "request": request,
        "active_menu": "anchor",
        "page_data": page_data,
        "keyword": keyword
    })

@router.post("/admin/api/upload_avatar")
async def upload_avatar(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    
    if not file.content_type or not file.content_type.startswith('image/'):
        return {"code": 400, "msg": "只支持图片文件"}
    
    try:
        file_bytes = await file.read()

        upload_bytes = file_bytes
        upload_filename = file.filename
        if file.content_type and file.content_type.startswith('image/'):
            try:
                comp = compress_image(file_bytes, max_width=480, quality=85)
                upload_bytes = comp.get("bytes", file_bytes)
                base = file.filename.rsplit('.', 1)[0] if '.' in file.filename else file.filename
                ext = comp.get("ext") or (file.filename.rsplit('.', 1)[-1] if '.' in file.filename else '')
                upload_filename = f"{base}.{ext}" if ext else upload_filename
            except Exception as e:
                print(f"Avatar compress failed, uploading original image: {e}")

        r2_client = R2Client()
        link_info = await r2_client.upload_and_get_link(upload_bytes, upload_filename)
        
        return {
            "code": 200,
            "msg": "上传成功",
            "avatar_url": link_info["url"]
        }
    except Exception as e:
        return {"code": 500, "msg": f"上传失败: {str(e)}"}

@router.post("/admin/api/add_anchor")
async def add_anchor(
    request: Request,
    nickname: str = Body(...),
    age: int = Body(0),
    avatar: str = Body(""),
    country: str = Body("US"),
    language_name: str = Body("English"),
    language_code: str = Body("en"),
    follow_count: int = Body(0),
    fans_count: int = Body(0),
    like_count: int = Body(0),
    is_review: bool = Body(False),
    tags: str = Body(""),
    db: AsyncSession = Depends(get_db),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    user_id = random.randint(1000000, 9999999) + 10000000
    new_anchor = models.AppUser(
        user_id=user_id,
        nickname=nickname,
        age=age,
        avatar=avatar,
        country=country,
        language_name=language_name,
        language_code=language_code,
        follow_count=follow_count,
        fans_count=fans_count,
        like_count=like_count,
        is_review=is_review,
        tags=tags,
        is_anchor=True
    )
    db.add(new_anchor)
    await db.commit()
    await db.refresh(new_anchor)
    return {
        "code": 200,
        "msg": "新增成功",
        "anchor": {
            "user_id": new_anchor.user_id,
            "nickname": new_anchor.nickname,
            "age": new_anchor.age,
            "avatar": new_anchor.avatar,
            "country": new_anchor.country,
            "language_name": new_anchor.language_name,
            "language_code": new_anchor.language_code,
            "follow_count": new_anchor.follow_count,
            "fans_count": new_anchor.fans_count,
            "like_count": new_anchor.like_count,
            "is_review": new_anchor.is_review,
            "tags": new_anchor.tags
        }
    }

@router.put("/admin/api/update_anchor")
async def update_anchor(
    request: Request,
    user_id: int = Body(...),
    nickname: str = Body(None),
    age: int = Body(None),
    avatar: str = Body(None),
    country: str = Body(None),
    language_name: str = Body(None),
    language_code: str = Body(None),
    follow_count: int = Body(None),
    fans_count: int = Body(None),
    like_count: int = Body(None),
    is_review: bool = Body(None),
    tags: str = Body(None),
    db: AsyncSession = Depends(get_db),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    stmt = select(models.AppUser).where(models.AppUser.user_id == user_id, models.AppUser.is_anchor == True)
    result = await db.execute(stmt)
    anchor = result.scalar_one_or_none()
    if not anchor:
        return {"code": 404, "msg": "主播不存在"}

    if nickname is not None:
        anchor.nickname = nickname
    if age is not None:
        anchor.age = age
    if avatar is not None:
        anchor.avatar = avatar
    if country is not None:
        anchor.country = country
    if language_name is not None:
        anchor.language_name = language_name
    if language_code is not None:
        anchor.language_code = language_code
    if follow_count is not None:
        anchor.follow_count = follow_count
    if fans_count is not None:
        anchor.fans_count = fans_count
    if like_count is not None:
        anchor.like_count = like_count
    if is_review is not None:
        anchor.is_review = is_review
    if tags is not None:
        anchor.tags = tags

    await db.commit()
    await db.refresh(anchor)
    return {
        "code": 200,
        "msg": "更新成功",
        "anchor": {
            "user_id": anchor.user_id,
            "nickname": anchor.nickname,
            "age": anchor.age,
            "avatar": anchor.avatar,
            "country": anchor.country,
            "language_name": anchor.language_name,
            "language_code": anchor.language_code,
            "follow_count": anchor.follow_count,
            "fans_count": anchor.fans_count,
            "like_count": anchor.like_count,
            "is_review": anchor.is_review,
            "tags": anchor.tags
        }
    }

@router.delete("/admin/api/delete_anchor")
async def delete_anchor(
    request: Request,
    user_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    stmt = select(models.AppUser).where(models.AppUser.user_id == user_id, models.AppUser.is_anchor == True)
    result = await db.execute(stmt)
    anchor = result.scalar_one_or_none()
    if not anchor:
        return {"code": 404, "msg": "主播不存在"}
    db.delete(anchor)
    await db.commit()
    return {"code": 200, "msg": "删除成功"}
