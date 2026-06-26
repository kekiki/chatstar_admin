from fastapi import APIRouter, Request, Depends, Body, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
import models

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin/app_list", response_class=HTMLResponse)
async def app_list(request: Request, db: Session = Depends(get_db), _user=Depends(lambda: None)):
    from routers.auth import require_login
    _user = require_login(request, db)
    apps = db.query(models.AppList).all()
    tpl = templates.env.get_template("app_list.html")
    content = tpl.render({"request": request, "active_menu": "app_list", "apps": apps})
    return HTMLResponse(content)

@router.post("/admin/api/add_app_list")
async def add_app_list(
    app_name: str = Body(...),
    bound_id: str = Body(...),
    is_online: bool = Body(...),
    db: Session = Depends(get_db),
    _user = Depends(lambda: None)
):
    from routers.auth import require_login
    from fastapi import Request
    _user = require_login(Request, db)
    exist = db.query(models.AppList).filter(models.AppList.bound_id == bound_id).first()
    if exist:
        return {"code": 400, "msg": "包名已存在"}
    new_app = models.AppList(
        app_name=app_name,
        bound_id=bound_id,
        is_online=is_online
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return {
        "code": 200,
        "msg": "新增成功",
        "app": {
            "id": new_app.id,
            "app_name": new_app.app_name,
            "bound_id": new_app.bound_id,
            "is_online": new_app.is_online,
        }
    }

@router.put("/admin/api/update_app_list")
async def update_app_list(
    id: int = Body(...),
    app_name: str = Body(...),
    bound_id: str = Body(...),
    is_online: bool = Body(...),
    db: Session = Depends(get_db),
    _user = Depends(lambda: None)
):
    from routers.auth import require_login
    from fastapi import Request
    _user = require_login(Request, db)
    app_item = db.query(models.AppList).filter(models.AppList.id == id).first()
    if not app_item:
        return {"code": 404, "msg": "应用不存在"}
    duplicate = db.query(models.AppList).filter(models.AppList.bound_id == bound_id, models.AppList.id != id).first()
    if duplicate:
        return {"code": 400, "msg": "包名已存在"}
    app_item.app_name = app_name
    app_item.bound_id = bound_id
    app_item.is_online = is_online
    db.commit()
    db.refresh(app_item)
    return {
        "code": 200,
        "msg": "更新成功",
        "app": {
            "id": app_item.id,
            "app_name": app_item.app_name,
            "bound_id": app_item.bound_id,
            "is_online": app_item.is_online,
        }
    }

@router.delete("/admin/api/delete_app_list")
async def delete_app_list(
    id: int = Query(...),
    db: Session = Depends(get_db),
    _user = Depends(lambda: None)
):
    from routers.auth import require_login
    from fastapi import Request
    _user = require_login(Request, db)
    app_item = db.query(models.AppList).filter(models.AppList.id == id).first()
    if not app_item:
        return {"code": 404, "msg": "应用不存在"}
    db.delete(app_item)
    db.commit()
    return {"code": 200, "msg": "删除成功"}
