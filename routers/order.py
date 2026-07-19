from fastapi import APIRouter, Request, Depends, Query, Body
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from tools import get_page_params, paginate_query
import models
import io
import datetime

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def datetime_format(timestamp):
    if not timestamp:
        return ""
    try:
        dt = datetime.datetime.fromtimestamp(int(timestamp))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(timestamp)

templates.env.filters["datetime_format"] = datetime_format

@router.get("/admin/order", response_class=HTMLResponse)
async def order_list(
    request: Request,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1),
    page_size: int = Query(10),
    keyword: str = Query("", description="全字段模糊搜索"),
    status: int = Query(-1),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    page, page_size, offset = get_page_params(page, page_size)
    q = select(models.PayOrder)

    if keyword:
        q = q.where(
            or_(
                models.PayOrder.id.like(f"%{keyword}%"),
                models.PayOrder.user_id.like(f"%{keyword}%"),
                models.PayOrder.order_no.like(f"%{keyword}%")
            )
        )
    if status in (0, 1, 2):
        q = q.where(models.PayOrder.order_status == status)

    page_data = await paginate_query(db, q, offset, page_size)

    app_result = await db.execute(select(models.AppList))
    app_name_map = {
        app.package_name: app.app_name
        for app in app_result.scalars().all()
        if getattr(app, "package_name", None)
    }

    product_result = await db.execute(select(models.Product))
    product_price_map = {}
    for product in product_result.scalars().all():
        if getattr(product, "package_name", None) and getattr(product, "sku", None):
            product_price_map[(product.package_name, product.sku)] = product.currency_price

    return templates.TemplateResponse(request, "order_list.html", {
        "request": request,
        "active_menu": "order",
        "page_data": page_data,
        "keyword": keyword,
        "status": status,
        "app_name_map": app_name_map,
        "product_price_map": product_price_map,
    })

@router.get("/admin/order/export")
async def export_order(
    request: Request,
    db: AsyncSession = Depends(get_db),
    keyword: str = Query(""),
    status: int = Query(-1),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    q = select(models.PayOrder)
    if keyword:
        q = q.where(
            or_(
                models.PayOrder.id.like(f"%{keyword}%"),
                models.PayOrder.user_id.like(f"%{keyword}%"),
                models.PayOrder.order_no.like(f"%{keyword}%")
            )
        )
    if status in (0, 1, 2):
        q = q.where(models.PayOrder.order_status == status)
    result = await db.execute(q)
    order_list = result.scalars().all()

    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "订单数据"
    header = ["订单ID", "用户ID", "订单号", "创建时间", "SKU", "折扣类型", "订单状态", "货币代码", "货币价格"]
    ws.append(header)
    for od in order_list:
        status_text = {0: "待支付", 1: "支付成功", 2: "支付失败"}.get(od.order_status, "未知")
        discount_text = {0: "普通折扣", 1: "首充折扣"}.get(od.discount_type, "未知")
        row = [od.id, od.user_id, od.order_no, od.created_time, od.sku, discount_text, status_text, od.currency_code, od.currency_price]
        ws.append(row)

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)
    return StreamingResponse(
        io.BytesIO(stream.read()),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="订单列表.xlsx"'}
    )
