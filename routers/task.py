from fastapi import APIRouter, Request, Depends, Query, Body, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, or_, cast, String
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from tools import get_page_params, paginate_query
from r2_client import R2Client
from image_utils import compress_image
import models

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin/task", response_class=HTMLResponse)
async def task_list(
    request: Request,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1),
    page_size: int = Query(20),
    keyword: str = Query("", description="全字段模糊搜索"),
    category: int = Query(-1, description="任务分类筛选"),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    page, page_size, offset = get_page_params(page, page_size)
    q = select(models.Task).order_by(models.Task.category.asc(), models.Task.id.asc())

    if keyword:
        q = q.where(
            or_(
                cast(models.Task.id, String).like(f"%{keyword}%"),
                models.Task.name.like(f"%{keyword}%"),
                models.Task.desc.like(f"%{keyword}%")
            )
        )

    if category >= 0:
        q = q.where(models.Task.category == category)

    page_data = await paginate_query(db, q, offset, page_size)
    return templates.TemplateResponse(request, "task_list.html", {
        "request": request,
        "active_menu": "task",
        "page_data": page_data,
        "keyword": keyword,
        "category": category
    })

@router.post("/admin/api/upload_task_icon")
async def upload_task_icon(
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
        file_content_type = file.content_type

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

@router.post("/admin/api/add_task")
async def add_task(
    request: Request,
    name: str = Body(""),
    desc: str = Body(""),
    icon: str = Body(""),
    num: int = Body(0),
    category: int = Body(0),
    type: str = Body(""),
    diamonds: int = Body(0),
    call_card_num: int = Body(0),
    match_card_num: int = Body(0),
    chat_card_num: int = Body(0),
    db: AsyncSession = Depends(get_db),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)

    if not name:
        return {"code": 400, "msg": "请填写任务名称"}

    new_task = models.Task(
        name=name, desc=desc, icon=icon, num=num,
        category=category, type=type, diamonds=diamonds,
        call_card_num=call_card_num, match_card_num=match_card_num, chat_card_num=chat_card_num
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return {"code": 200, "msg": "新增成功"}

@router.put("/admin/api/update_task")
async def update_task(
    request: Request,
    id: int = Body(...),
    name: str = Body(""),
    desc: str = Body(""),
    icon: str = Body(""),
    num: int = Body(0),
    category: int = Body(0),
    type: str = Body(""),
    diamonds: int = Body(0),
    call_card_num: int = Body(0),
    match_card_num: int = Body(0),
    chat_card_num: int = Body(0),
    db: AsyncSession = Depends(get_db),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    stmt = select(models.Task).where(models.Task.id == id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    if not task:
        return {"code": 404, "msg": "任务不存在"}

    if name:
        task.name = name
    task.desc = desc
    task.icon = icon
    task.num = num
    task.category = category
    task.type = type
    task.diamonds = diamonds
    task.call_card_num = call_card_num
    task.match_card_num = match_card_num
    task.chat_card_num = chat_card_num

    await db.commit()
    await db.refresh(task)
    return {"code": 200, "msg": "更新成功"}

@router.delete("/admin/api/delete_task")
async def delete_task(
    request: Request,
    id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    stmt = select(models.Task).where(models.Task.id == id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    if not task:
        return {"code": 404, "msg": "任务不存在"}
    db.delete(task)
    await db.commit()
    return {"code": 200, "msg": "删除成功"}
