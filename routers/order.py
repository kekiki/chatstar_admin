from fastapi import APIRouter, Request, Depends, Query, Body
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from tools import get_page_params, paginate_query
import models
import io

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin/order", response_class=HTMLResponse)
async def order_list(
    request: Request,
    db: Session = Depends(get_db),
    page: int = Query(1),
    page_size: int = Query(10),
    keyword: str = Query("", description="全字段模糊搜索"),
    start_date: str = Query(""),
    end_date: str = Query(""),
    status: int = Query(-1),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    page, page_size, offset = get_page_params(page, page_size)
    q = db.query(models.PayOrder)

    if keyword:
        q = q.filter(
            or_(
                models.PayOrder.id.like(f"%{keyword}%"),
                models.PayOrder.app_id.like(f"%{keyword}%"),
                models.PayOrder.user_id.like(f"%{keyword}%"),
                models.PayOrder.pay_amount.like(f"%{keyword}%"),
                models.PayOrder.pay_time.like(f"%{keyword}%")
            )
        )
    if start_date:
        q = q.filter(models.PayOrder.pay_time >= start_date)
    if end_date:
        q = q.filter(models.PayOrder.pay_time <= f"{end_date} 23:59:59")
    if status in (0, 1):
        q = q.filter(models.PayOrder.status == status)

    page_data = paginate_query(db, q, offset, page_size)
    return templates.TemplateResponse(request, "order_list.html", {
        "request": request,
        "active_menu": "order",
        "page_data": page_data,
        "keyword": keyword,
        "start_date": start_date,
        "end_date": end_date,
        "status": status
    })

@router.get("/admin/order/export")
async def export_order(
    request: Request,
    db: Session = Depends(get_db),
    keyword: str = Query(""),
    start_date: str = Query(""),
    end_date: str = Query(""),
    status: int = Query(-1),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    q = db.query(models.PayOrder)
    if keyword:
        q = q.filter(
            or_(
                models.PayOrder.id.like(f"%{keyword}%"),
                models.PayOrder.app_id.like(f"%{keyword}%"),
                models.PayOrder.user_id.like(f"%{keyword}%"),
                models.PayOrder.pay_amount.like(f"%{keyword}%"),
                models.PayOrder.pay_time.like(f"%{keyword}%")
            )
        )
    if start_date:
        q = q.filter(models.PayOrder.pay_time >= start_date)
    if end_date:
        q = q.filter(models.PayOrder.pay_time <= f"{end_date} 23:59:59")
    if status in (0, 1):
        q = q.filter(models.PayOrder.status == status)
    order_list = q.all()

    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "订单数据"
    header = ["订单ID", "应用ID", "用户ID", "支付金额", "支付时间", "订单状态"]
    ws.append(header)
    for od in order_list:
        stat_text = "已支付" if od.status == 1 else "未支付"
        row = [od.id, od.app_id, od.user_id, od.pay_amount, od.pay_time, stat_text]
        ws.append(row)

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)
    return StreamingResponse(
        io.BytesIO(stream.read()),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="订单列表.xlsx"'}
    )
