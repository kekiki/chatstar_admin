from fastapi import APIRouter, Request, Depends, Body, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
import models

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin/app_list", response_class=HTMLResponse)
async def app_list(request: Request, db: AsyncSession = Depends(get_db), _user=Depends(lambda: None)):
    from routers.auth import require_login
    _user = require_login(request, db)
    stmt = select(models.AppList)
    result = await db.execute(stmt)
    apps = result.scalars().all()
    tpl = templates.env.get_template("app_list.html")
    content = tpl.render({"request": request, "active_menu": "app_list", "apps": apps})
    return HTMLResponse(content)

@router.post("/admin/api/add_app_list")
async def add_app_list(
    request: Request,
    app_name: str = Body(...),
    package_name: str = Body(...),
    is_online: bool = Body(...),
    db: AsyncSession = Depends(get_db),
    _user = Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    stmt = select(models.AppList).where(models.AppList.package_name == package_name)
    result = await db.execute(stmt)
    exist = result.scalar_one_or_none()
    if exist:
        return {"code": 400, "msg": "包名已存在"}
    new_app = models.AppList(
        app_name=app_name,
        package_name=package_name,
        is_online=is_online
    )
    db.add(new_app)
    await db.commit()
    await db.refresh(new_app)
    return {
        "code": 200,
        "msg": "新增成功",
        "app": {
            "id": new_app.id,
            "app_name": new_app.app_name,
            "package_name": new_app.package_name,
            "is_online": new_app.is_online,
        }
    }

@router.put("/admin/api/update_app_list")
async def update_app_list(
    request: Request,
    id: int = Body(...),
    app_name: str = Body(...),
    package_name: str = Body(...),
    is_online: bool = Body(...),
    db: AsyncSession = Depends(get_db),
    _user = Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    stmt = select(models.AppList).where(models.AppList.id == id)
    result = await db.execute(stmt)
    app_item = result.scalar_one_or_none()
    if not app_item:
        return {"code": 404, "msg": "应用不存在"}
    duplicate_stmt = select(models.AppList).where(models.AppList.package_name == package_name, models.AppList.id != id)
    duplicate_result = await db.execute(duplicate_stmt)
    duplicate = duplicate_result.scalar_one_or_none()
    if duplicate:
        return {"code": 400, "msg": "包名已存在"}
    app_item.app_name = app_name
    app_item.package_name = package_name
    app_item.is_online = is_online
    await db.commit()
    await db.refresh(app_item)
    return {
        "code": 200,
        "msg": "更新成功",
        "app": {
            "id": app_item.id,
            "app_name": app_item.app_name,
            "package_name": app_item.package_name,
            "is_online": app_item.is_online,
        }
    }

@router.delete("/admin/api/delete_app_list")
async def delete_app_list(
    request: Request,
    id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    _user = Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    stmt = select(models.AppList).where(models.AppList.id == id)
    result = await db.execute(stmt)
    app_item = result.scalar_one_or_none()
    if not app_item:
        return {"code": 404, "msg": "应用不存在"}
    db.delete(app_item)
    await db.commit()
    return {"code": 200, "msg": "删除成功"}
