from fastapi import APIRouter, Request, Depends, Body, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from tools import get_page_params, paginate_query
import models

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/admin/app_config", response_class=HTMLResponse)
async def app_config(
    request: Request,
    db: Session = Depends(get_db),
    page: int = Query(1),
    page_size: int = Query(10),
    package_name: str = Query(None, description="包名筛选"),
    app_version: str = Query("", description="版本号筛选"),
    review_package_name: str = Query(None, description="审核配置-应用筛选"),
    review_app_version: str = Query("", description="审核配置-版本筛选"),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    apps = db.query(models.AppList).all()

    page, page_size, offset = get_page_params(page, page_size)
    q = db.query(models.AppConfig)

    if package_name:
        q = q.filter(models.AppConfig.package_name == package_name)
    if app_version:
        q = q.filter(models.AppConfig.app_version.like(f"%{app_version}%"))

    page_data = paginate_query(db, q, offset, page_size)

    # Get AppReview data
    review_page, review_page_size, review_offset = get_page_params(page, page_size)
    review_q = db.query(models.AppReview)

    if review_package_name:
        review_q = review_q.filter(models.AppReview.package_name == review_package_name)
    if review_app_version:
        review_q = review_q.filter(models.AppReview.app_version.like(f"%{review_app_version}%"))

    review_page_data = paginate_query(db, review_q, review_offset, review_page_size)

    return templates.TemplateResponse(request, "app_config.html", {
        "request": request,
        "active_menu": "app_config",
        "apps": apps,
        "page_data": page_data,
        "package_name": package_name,
        "app_version": app_version,
        "review_page_data": review_page_data,
        "review_package_name": review_package_name,
        "review_app_version": review_app_version
    })

@router.post("/admin/api/add_app_config")
async def add_app_config(
    request: Request,
    package_name: str = Body(...),
    app_version: str = Body(...),
    config_json: str = Body(...),
    remark: str = Body(default=""),
    db: Session = Depends(get_db),
    _user = Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    new_app = models.AppConfig(
        package_name=package_name,
        app_version=app_version,
        config_json=config_json,
        remark=remark
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return {
        "code": 200,
        "msg": "新增成功",
        "config": {
            "id": new_app.id,
            "package_name": new_app.package_name,
            "app_version": new_app.app_version,
            "config_json": new_app.config_json,
            "remark": new_app.remark,
        }
    }

@router.put("/admin/api/update_app_config")
async def update_app_config(
    request: Request,
    id: int = Body(...),
    app_version: str = Body(...),
    config_json: str = Body(...),
    remark: str = Body(default=""),
    db: Session = Depends(get_db),
    _user = Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    config_item = db.query(models.AppConfig).filter(models.AppConfig.id == id).first()
    if not config_item:
        return {"code": 404, "msg": "配置不存在"}
    config_item.app_version = app_version
    config_item.config_json = config_json
    config_item.remark = remark
    db.commit()
    db.refresh(config_item)
    return {
        "code": 200,
        "msg": "更新成功",
        "config": {
            "id": config_item.id,
            "package_name": config_item.package_name,
            "app_version": config_item.app_version,
            "config_json": config_item.config_json,
            "remark": config_item.remark,
        }
    }

@router.delete("/admin/api/delete_app_config")
async def delete_app_config(
    request: Request,
    id: int = Query(...),
    db: Session = Depends(get_db),
    _user = Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    config_item = db.query(models.AppConfig).filter(models.AppConfig.id == id).first()
    if not config_item:
        return {"code": 404, "msg": "配置不存在"}
    db.delete(config_item)
    db.commit()
    return {"code": 200, "msg": "删除成功"}

@router.post("/admin/api/add_app_review")
async def add_app_review(
    request: Request,
    package_name: str = Body(...),
    app_version: str = Body(...),
    db: Session = Depends(get_db),
    _user = Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    new_review = models.AppReview(
        package_name=package_name,
        app_version=app_version
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return {
        "code": 200,
        "msg": "新增成功",
        "review": {
            "id": new_review.id,
            "package_name": new_review.package_name,
            "app_version": new_review.app_version,
        }
    }

@router.put("/admin/api/update_app_review")
async def update_app_review(
    request: Request,
    id: int = Body(...),
    package_name: str = Body(...),
    app_version: str = Body(...),
    db: Session = Depends(get_db),
    _user = Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    review_item = db.query(models.AppReview).filter(models.AppReview.id == id).first()
    if not review_item:
        return {"code": 404, "msg": "审核配置不存在"}
    review_item.package_name = package_name
    review_item.app_version = app_version
    db.commit()
    db.refresh(review_item)
    return {
        "code": 200,
        "msg": "更新成功",
        "review": {
            "id": review_item.id,
            "package_name": review_item.package_name,
            "app_version": review_item.app_version,
        }
    }

@router.delete("/admin/api/delete_app_review")
async def delete_app_review(
    request: Request,
    id: int = Query(...),
    db: Session = Depends(get_db),
    _user = Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    review_item = db.query(models.AppReview).filter(models.AppReview.id == id).first()
    if not review_item:
        return {"code": 404, "msg": "审核配置不存在"}
    db.delete(review_item)
    db.commit()
    return {"code": 200, "msg": "删除成功"}