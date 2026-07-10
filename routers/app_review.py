from fastapi import APIRouter, Request, Depends, Body, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
import models

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin/app_review", response_class=HTMLResponse)
async def app_review(request: Request, db: Session = Depends(get_db), _user=Depends(lambda: None)):
    from routers.auth import require_login
    _user = require_login(request, db)
    reviews = db.query(models.AppReview).all()
    tpl = templates.env.get_template("app_review.html")
    content = tpl.render({"request": request, "active_menu": "app_review", "reviews": reviews})
    return HTMLResponse(content)

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