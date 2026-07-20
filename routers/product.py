from fastapi import APIRouter, Request, Depends, Query, Body
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, or_, cast, String
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from tools import get_page_params, paginate_query
import models

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin/product", response_class=HTMLResponse)
async def product_list(
    request: Request,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1),
    page_size: int = Query(10),
    keyword: str = Query("", description="全字段模糊搜索"),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    apps_stmt = select(models.AppList)
    apps_result = await db.execute(apps_stmt)
    apps = apps_result.scalars().all()
    page, page_size, offset = get_page_params(page, page_size)
    q = select(models.Product)

    if keyword:
        q = q.where(
            or_(
                cast(models.Product.id, String).like(f"%{keyword}%"),
                models.Product.package_name.like(f"%{keyword}%"),
                models.Product.sku.like(f"%{keyword}%"),
                models.Product.currency_code.like(f"%{keyword}%")
            )
        )

    page_data = await paginate_query(db, q, offset, page_size)
    return templates.TemplateResponse(request, "product_list.html", {
        "request": request,
        "active_menu": "product",
        "apps": apps,
        "page_data": page_data,
        "keyword": keyword
    })

@router.post("/admin/api/add_product")
async def add_product(
    request: Request,
    package_name: str = Body(""),
    sku: str = Body(""),
    diamonds: int = Body(0),
    vip_days: int = Body(0),
    reward_diamonds: int = Body(0),
    discount_type: int = Body(0),
    discount: int = Body(100),
    currency_code: str = Body("USD"),
    currency_price: float = Body(0),
    call_card_num: int = Body(0),
    match_card_num: int = Body(0),
    chat_card_num: int = Body(0),
    db: AsyncSession = Depends(get_db),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    
    if not package_name:
        return {"code": 400, "msg": "请填写应用包名"}
    if not sku:
        return {"code": 400, "msg": "请填写SKU"}
    
    new_product = models.Product(
        package_name=package_name,
        sku=sku,
        diamonds=diamonds,
        vip_days=vip_days,
        reward_diamonds=reward_diamonds,
        discount_type=discount_type,
        discount=discount,
        currency_code=currency_code,
        currency_price=currency_price,
        call_card_num=call_card_num,
        match_card_num=match_card_num,
        chat_card_num=chat_card_num
    )
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return {
        "code": 200,
        "msg": "新增成功",
        "product": {
            "id": new_product.id,
            "package_name": new_product.package_name,
            "sku": new_product.sku,
            "diamonds": new_product.diamonds,
            "vip_days": new_product.vip_days,
            "reward_diamonds": new_product.reward_diamonds,
            "discount_type": new_product.discount_type,
            "discount": new_product.discount,
            "currency_code": new_product.currency_code,
            "currency_price": new_product.currency_price,
            "call_card_num": new_product.call_card_num,
            "match_card_num": new_product.match_card_num,
            "chat_card_num": new_product.chat_card_num
        }
    }

@router.put("/admin/api/update_product")
async def update_product(
    request: Request,
    id: int = Body(...),
    package_name: str = Body(""),
    sku: str = Body(""),
    diamonds: int = Body(0),
    vip_days: int = Body(0),
    reward_diamonds: int = Body(0),
    discount_type: int = Body(0),
    discount: int = Body(100),
    currency_code: str = Body("USD"),
    currency_price: float = Body(0),
    call_card_num: int = Body(0),
    match_card_num: int = Body(0),
    chat_card_num: int = Body(0),
    db: AsyncSession = Depends(get_db),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    stmt = select(models.Product).where(models.Product.id == id)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if not product:
        return {"code": 404, "msg": "商品不存在"}
    
    if package_name:
        product.package_name = package_name
    if sku:
        product.sku = sku
    if diamonds is not None:
        product.diamonds = diamonds
    if vip_days is not None:
        product.vip_days = vip_days
    if reward_diamonds is not None:
        product.reward_diamonds = reward_diamonds
    if discount_type is not None:
        product.discount_type = discount_type
    if discount is not None:
        product.discount = discount
    if currency_code:
        product.currency_code = currency_code
    if currency_price is not None:
        product.currency_price = currency_price
    if call_card_num is not None:
        product.call_card_num = call_card_num
    if match_card_num is not None:
        product.match_card_num = match_card_num
    if chat_card_num is not None:
        product.chat_card_num = chat_card_num
    
    await db.commit()
    await db.refresh(product)
    return {
        "code": 200,
        "msg": "更新成功",
        "product": {
            "id": product.id,
            "package_name": product.package_name,
            "sku": product.sku,
            "diamonds": product.diamonds,
            "vip_days": product.vip_days,
            "reward_diamonds": product.reward_diamonds,
            "discount_type": product.discount_type,
            "discount": product.discount,
            "currency_code": product.currency_code,
            "currency_price": product.currency_price,
            "call_card_num": product.call_card_num,
            "match_card_num": product.match_card_num,
            "chat_card_num": product.chat_card_num
        }
    }

@router.delete("/admin/api/delete_product")
async def delete_product(
    request: Request,
    id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    _user=Depends(lambda: None)
):
    from routers.auth import require_login
    _user = require_login(request, db)
    stmt = select(models.Product).where(models.Product.id == id)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if not product:
        return {"code": 404, "msg": "商品不存在"}
    db.delete(product)
    await db.commit()
    return {"code": 200, "msg": "删除成功"}
