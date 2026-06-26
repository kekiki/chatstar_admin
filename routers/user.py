from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from tools import get_page_params, paginate_query
import models

router = APIRouter()
templates = Jinja2Templates(directory="templates")

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
    page, page_size, offset = get_page_params(page, page_size)
    q = db.query(models.AppUser)

    if keyword:
        q = q.filter(
            or_(
                models.AppUser.id.like(f"%{keyword}%"),
                models.AppUser.app_id.like(f"%{keyword}%"),
                models.AppUser.register_time.like(f"%{keyword}%"),
                models.AppUser.last_login.like(f"%{keyword}%")
            )
        )
    if start_date:
        q = q.filter(models.AppUser.register_time >= start_date)
    if end_date:
        q = q.filter(models.AppUser.register_time <= f"{end_date} 23:59:59")

    page_data = paginate_query(db, q, offset, page_size)
    return templates.TemplateResponse(request, "user_list.html", {
        "request": request,
        "active_menu": "user",
        "page_data": page_data,
        "keyword": keyword,
        "start_date": start_date,
        "end_date": end_date
    })
