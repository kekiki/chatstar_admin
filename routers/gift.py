from fastapi import APIRouter, Request, Depends, Query, Body, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, or_, cast, String
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from tools import get_page_params, paginate_query
import models
import os
import tempfile
from r2_client import R2Client
from image_utils import compress_image

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin/gift", response_class=HTMLResponse)
async def gift_list(
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
    q = select(models.Gift).order_by(models.Gift.gift_price.asc())

    if keyword:
        q = q.where(
            or_(
                cast(models.Gift.id, String).like(f"%{keyword}%"),
                models.Gift.gift_name.like(f"%{keyword}%")
            )
        )

    page_data = await paginate_query(db, q, offset, page_size)
    return templates.TemplateResponse(request, "gift_list.html", {
        "request": request,
        "active_menu": "gift",
        "page_data": page_data,
        "keyword": keyword
    })

@router.post("/admin/api/upload_gift_icon")
async def upload_gift_icon(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    
    # 检查文件类型
    if not file.content_type or not file.content_type.startswith('image/'):
        return {"code": 400, "msg": "只支持图片文件"}
    
    try:
        # 读取文件内容
        file_bytes = await file.read()
        file_content_type = file.content_type

        # 图片压缩
        upload_bytes = file_bytes
        upload_content_type = file_content_type
        upload_filename = file.filename
        try:
            comp = compress_image(file_bytes, max_width=480, quality=85)
            upload_bytes = comp.get("bytes", file_bytes)
            upload_content_type = comp.get("content_type", file_content_type)
            base = file.filename.rsplit('.', 1)[0] if '.' in file.filename else file.filename
            ext = comp.get("ext") or (file.filename.rsplit('.', 1)[-1] if '.' in file.filename else '')
            upload_filename = f"{base}.{ext}" if ext else upload_filename
        except Exception as e:
            print(f"Image compress failed, will upload original: {e}")

        r2_client = R2Client()
        link_info = await r2_client.upload_and_get_link(upload_bytes, upload_filename, upload_content_type)
        
        return {
            "code": 200,
            "msg": "上传成功",
            "url": link_info["url"]
        }
    except Exception as e:
        return {"code": 500, "msg": f"上传失败: {str(e)}"}

@router.post("/admin/api/upload_gift_animation")
async def upload_gift_animation(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    
    # 检查文件类型
    if not file.content_type or (not file.content_type.startswith('image/') and not file.content_type.startswith('video/')):
        return {"code": 400, "msg": "只支持图片或视频文件"}
    
    try:
        # 读取文件内容
        file_bytes = await file.read()
        file_content_type = file.content_type

        # 如果是图片，进行压缩
        upload_bytes = file_bytes
        upload_content_type = file_content_type
        upload_filename = file.filename
        if file_content_type and file_content_type.startswith('image/'):
            try:
                comp = compress_image(file_bytes, max_width=480, quality=85)
                upload_bytes = comp.get("bytes", file_bytes)
                upload_content_type = comp.get("content_type", file_content_type)
                base = file.filename.rsplit('.', 1)[0] if '.' in file.filename else file.filename
                ext = comp.get("ext") or (file.filename.rsplit('.', 1)[-1] if '.' in file.filename else '')
                upload_filename = f"{base}.{ext}" if ext else upload_filename
            except Exception as e:
                print(f"Image compress failed, will upload original: {e}")

        r2_client = R2Client()
        link_info = await r2_client.upload_and_get_link(upload_bytes, upload_filename, upload_content_type)
        
        return {
            "code": 200,
            "msg": "上传成功",
            "url": link_info["url"]
        }
    except Exception as e:
        return {"code": 500, "msg": f"上传失败: {str(e)}"}

@router.post("/admin/api/add_gift")
async def add_gift(
    request: Request,
    gift_name: str = Body(""),
    gift_icon: str = Body(""),
    gift_price: int = Body(0),
    gift_animation: str = Body(""),
    db: AsyncSession = Depends(get_db),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    
    if not gift_name:
        return {"code": 400, "msg": "请填写礼物名称"}
    if not gift_icon:
        return {"code": 400, "msg": "请上传礼物图标"}
    
    new_gift = models.Gift(
        gift_name=gift_name,
        gift_icon=gift_icon,
        gift_price=gift_price,
        gift_animation=gift_animation
    )
    db.add(new_gift)
    await db.commit()
    await db.refresh(new_gift)
    return {
        "code": 200,
        "msg": "新增成功",
        "gift": {
            "id": new_gift.id,
            "gift_name": new_gift.gift_name,
            "gift_icon": new_gift.gift_icon,
            "gift_price": new_gift.gift_price,
            "gift_animation": new_gift.gift_animation
        }
    }

@router.put("/admin/api/update_gift")
async def update_gift(
    request: Request,
    id: int = Body(...),
    gift_name: str = Body(""),
    gift_icon: str = Body(""),
    gift_price: int = Body(0),
    gift_animation: str = Body(""),
    db: AsyncSession = Depends(get_db),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    stmt = select(models.Gift).where(models.Gift.id == id)
    result = await db.execute(stmt)
    gift = result.scalar_one_or_none()
    if not gift:
        return {"code": 404, "msg": "礼物不存在"}
    
    if gift_name:
        gift.gift_name = gift_name
    if gift_icon:
        gift.gift_icon = gift_icon
    if gift_price is not None:
        gift.gift_price = gift_price
    if gift_animation:
        gift.gift_animation = gift_animation
    
    await db.commit()
    await db.refresh(gift)
    return {
        "code": 200,
        "msg": "更新成功",
        "gift": {
            "id": gift.id,
            "gift_name": gift.gift_name,
            "gift_icon": gift.gift_icon,
            "gift_price": gift.gift_price,
            "gift_animation": gift.gift_animation
        }
    }

@router.delete("/admin/api/delete_gift")
async def delete_gift(
    request: Request,
    id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    stmt = select(models.Gift).where(models.Gift.id == id)
    result = await db.execute(stmt)
    gift = result.scalar_one_or_none()
    if not gift:
        return {"code": 404, "msg": "礼物不存在"}
    db.delete(gift)
    await db.commit()
    return {"code": 200, "msg": "删除成功"}
