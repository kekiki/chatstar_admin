from typing import Literal

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import String, cast, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.black_white import BlackWhiteDevice, BlackWhiteIp, BlackWhiteStatus, BlackWhiteUser
from routers.auth import require_login
from tools import get_page_params, paginate_query

router = APIRouter()
templates = Jinja2Templates(directory="templates")

LIST_TYPES = {
    "user": (BlackWhiteUser, BlackWhiteUser.user_id, "用户", "用户 ID"),
    "ip": (BlackWhiteIp, BlackWhiteIp.ip, "IP", "IP 地址"),
    "device": (BlackWhiteDevice, BlackWhiteDevice.device_id, "设备", "设备 ID"),
}
STATUS_LABELS = {
    BlackWhiteStatus.REVIEW: ("审核", "text-bg-warning"),
    BlackWhiteStatus.BLACK: ("黑名单", "text-bg-danger"),
    BlackWhiteStatus.WHITE: ("白名单", "text-bg-info"),
}


@router.get("/admin/black_white", response_class=HTMLResponse, dependencies=[Depends(require_login)])
async def black_white_list(
    request: Request,
    db: AsyncSession = Depends(get_db),
    kind: Literal["user", "ip", "device"] = "user",
    status: int = Query(-1, ge=-1, le=BlackWhiteStatus.WHITE),
    keyword: str = Query(""),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    model, identifier, _, identifier_label = LIST_TYPES[kind]
    query = select(model).order_by(model.created_time.desc().nulls_last(), model.id.desc())
    if status in STATUS_LABELS:
        query = query.where(model.status == status)
    keyword = keyword.strip()
    if keyword:
        search_column = cast(identifier, String) if kind == "user" else identifier
        query = query.where(search_column.contains(keyword, autoescape=True))

    _, _, offset = get_page_params(page, page_size)
    page_data = await paginate_query(db, query, offset, page_size)

    return templates.TemplateResponse(request, "black_white_list.html", {
        "active_menu": "black_white",
        "list_types": {key: config[2] for key, config in LIST_TYPES.items()},
        "kind": kind,
        "identifier_key": identifier.key,
        "identifier_label": identifier_label,
        "status_labels": STATUS_LABELS,
        "status": status,
        "keyword": keyword,
        "page_data": page_data,
    })
