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

@router.get("/admin/anchor", response_class=HTMLResponse)
async def anchor_list(
    request: Request,
    db: Session = Depends(get_db),
    page: int = Query(1),
    page_size: int = Query(10),
    keyword: str = Query("", description="全字段模糊搜索"),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    page, page_size, offset = get_page_params(page, page_size)
    q = db.query(models.Anchor)

    if keyword:
        q = q.filter(
            or_(
                models.Anchor.id.like(f"%{keyword}%"),
                models.Anchor.nickname.like(f"%{keyword}%"),
                models.Anchor.country.like(f"%{keyword}%"),
                models.Anchor.language_name.like(f"%{keyword}%"),
                models.Anchor.language_code.like(f"%{keyword}%")
            )
        )

    page_data = paginate_query(db, q, offset, page_size)
    return templates.TemplateResponse(request, "anchor_list.html", {
        "request": request,
        "active_menu": "anchor",
        "page_data": page_data,
        "keyword": keyword
    })
