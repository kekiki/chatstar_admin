from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import UserReport
from routers.auth import require_login
from tools import get_page_params, paginate_query

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/admin/user_report", response_class=HTMLResponse, dependencies=[Depends(require_login)])
async def user_report_list(
    request: Request,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    _, _, offset = get_page_params(page, page_size)
    query = select(UserReport).order_by(UserReport.created_time.desc().nulls_last(), UserReport.id.desc())
    page_data = await paginate_query(db, query, offset, page_size)

    return templates.TemplateResponse(request, "user_report_list.html", {
        "active_menu": "user_report",
        "page_data": page_data,
    })
