from fastapi import APIRouter, Request, Depends, Body, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
import models

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin/app_config", response_class=HTMLResponse)
async def app_config_list(request: Request, db: AsyncSession = Depends(get_db), _user=Depends(lambda: None)):
    from routers.auth import require_login
    _user = require_login(request, db)
    stmt = select(models.AppConfig).order_by(models.AppConfig.id.desc())
    result = await db.execute(stmt)
    configs = result.scalars().all()
    app_stmt = select(models.AppList).order_by(models.AppList.id)
    app_result = await db.execute(app_stmt)
    apps = app_result.scalars().all()
    tpl = templates.env.get_template("app_config_list.html")
    content = tpl.render({"request": request, "active_menu": "app_config", "configs": configs, "apps": apps})
    return HTMLResponse(content)

@router.post("/admin/api/add_app_config")
async def add_app_config(
    request: Request,
    package_name: str = Body(...),
    app_version: str = Body(""),
    key: str = Body(...),
    value: str = Body(""),
    remark: str = Body(""),
    db: AsyncSession = Depends(get_db),
    _user = Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    stmt = select(models.AppConfig).where(models.AppConfig.package_name == package_name, models.AppConfig.key == key)
    result = await db.execute(stmt)
    exist = result.scalar_one_or_none()
    if exist:
        return {"code": 400, "msg": "该包名下已存在相同key的配置"}
    new_config = models.AppConfig(
        package_name=package_name,
        app_version=app_version,
        key=key,
        value=value,
        remark=remark
    )
    db.add(new_config)
    await db.commit()
    await db.refresh(new_config)
    return {
        "code": 200,
        "msg": "新增成功",
        "config": {
            "id": new_config.id,
            "package_name": new_config.package_name,
            "app_version": new_config.app_version,
            "key": new_config.key,
            "value": new_config.value,
            "remark": new_config.remark,
        }
    }

@router.put("/admin/api/update_app_config")
async def update_app_config(
    request: Request,
    id: int = Body(...),
    package_name: str = Body(...),
    app_version: str = Body(""),
    key: str = Body(...),
    value: str = Body(""),
    remark: str = Body(""),
    db: AsyncSession = Depends(get_db),
    _user = Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    stmt = select(models.AppConfig).where(models.AppConfig.id == id)
    result = await db.execute(stmt)
    config_item = result.scalar_one_or_none()
    if not config_item:
        return {"code": 404, "msg": "配置不存在"}
    duplicate_stmt = select(models.AppConfig).where(models.AppConfig.package_name == package_name, models.AppConfig.key == key, models.AppConfig.id != id)
    duplicate_result = await db.execute(duplicate_stmt)
    duplicate = duplicate_result.scalar_one_or_none()
    if duplicate:
        return {"code": 400, "msg": "该包名下已存在相同key的配置"}
    config_item.package_name = package_name
    config_item.app_version = app_version
    config_item.key = key
    config_item.value = value
    config_item.remark = remark
    await db.commit()
    await db.refresh(config_item)
    return {
        "code": 200,
        "msg": "更新成功",
        "config": {
            "id": config_item.id,
            "package_name": config_item.package_name,
            "app_version": config_item.app_version,
            "key": config_item.key,
            "value": config_item.value,
            "remark": config_item.remark,
        }
    }

@router.delete("/admin/api/delete_app_config")
async def delete_app_config(
    request: Request,
    id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    _user = Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    stmt = select(models.AppConfig).where(models.AppConfig.id == id)
    result = await db.execute(stmt)
    config_item = result.scalar_one_or_none()
    if not config_item:
        return {"code": 404, "msg": "配置不存在"}
    db.delete(config_item)
    await db.commit()
    return {"code": 200, "msg": "删除成功"}
