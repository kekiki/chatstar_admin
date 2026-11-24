from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import and_, case, distinct, func, or_, select, union_all
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import AppList, AppUser, DailyStat, DailyUserActivity, PayOrder, Product
from routers.auth import require_login

router = APIRouter()
templates = Jinja2Templates(directory="templates")
# Must match the reporting timezone used by chatstar_api/app/activity.py.
REPORT_TZ = ZoneInfo("Asia/Shanghai")


def report_day_bounds(day: date) -> tuple[int, int]:
    start = datetime.combine(day, time.min, REPORT_TZ)
    end = datetime.combine(day + timedelta(days=1), time.min, REPORT_TZ)
    return int(start.timestamp()), int(end.timestamp())


def percentage(count: int, total: int | None) -> float | None:
    return round(count * 100 / total, 2) if total else None


def paid_orders(start: int, end: int, package: str, country: str):
    # Older Google orders have no recorded price. Use the configured product
    # price, taking one row per package, SKU and type to avoid multiplying sales.
    product_id = (
        select(Product.id)
        .where(
            Product.package_name == PayOrder.package_name,
            Product.sku == PayOrder.sku,
            Product.type == PayOrder.type,
        )
        .order_by(Product.id.desc())
        .limit(1)
        .correlate(PayOrder)
        .scalar_subquery()
    )
    has_order_price = PayOrder.currency_price > 0
    amount = case((has_order_price, PayOrder.currency_price), else_=Product.currency_price)
    currency = case((has_order_price, PayOrder.currency_code), else_=Product.currency_code)
    channel = func.coalesce(
        func.nullif(func.trim(PayOrder.pp_type), ""),
        case((PayOrder.pp_id == 1, "Google"), else_="其他"),
    )
    paid_on_day = or_(
        and_(PayOrder.updated_time >= start, PayOrder.updated_time < end, PayOrder.updated_time != 0),
        and_(
            or_(PayOrder.updated_time.is_(None), PayOrder.updated_time == 0),
            PayOrder.created_time >= start, PayOrder.created_time < end,
        ),
    )
    query = (
        select(
            PayOrder.package_name.label("package"),
            PayOrder.user_id,
            and_(AppUser.created_time >= start, AppUser.created_time < end).label("is_new"),
            amount.label("amount"),
            func.upper(func.nullif(func.trim(currency), "")).label("currency"),
            channel.label("channel"),
        )
        .outerjoin(AppUser, AppUser.user_id == PayOrder.user_id)
        .outerjoin(Product, and_(or_(PayOrder.currency_price <= 0, PayOrder.currency_price.is_(None)), Product.id == product_id))
        .where(
            PayOrder.package_name.is_not(None), PayOrder.order_status == 1,
            paid_on_day, AppUser.is_anchor.is_not(True),
        )
    )
    if package:
        query = query.where(PayOrder.package_name == package)
    if country:
        query = query.where(AppUser.country == country)
    return query.cte("paid_orders")


@router.get("/admin/dashboard", response_class=HTMLResponse, dependencies=[Depends(require_login)])
async def dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    stat_date: date | None = Query(None, alias="date", ge=date(1970, 1, 1), le=date(9999, 12, 30)),
    package: str = Query("", max_length=100),
    country: str = Query("", max_length=64),
    currency: str = Query("", pattern=r"^(?:[A-Z]{3})?$"),
):
    today = datetime.now(REPORT_TZ).date()
    day = stat_date or today
    start, end = report_day_bounds(day)
    apps = (await db.scalars(select(AppList).order_by(AppList.app_name, AppList.package_name))).all()
    countries = (await db.scalars(
        select(AppUser.country).where(
            AppUser.country.is_not(None), AppUser.country != "", AppUser.is_anchor.is_not(True)
        ).distinct().order_by(AppUser.country)
    )).all()

    users = select(AppUser.package_name.label("package"), AppUser.user_id).where(
        AppUser.is_anchor.is_not(True), AppUser.package_name.is_not(None), AppUser.user_id.is_not(None),
    )
    if package:
        users = users.where(AppUser.package_name == package)
    if country:
        users = users.where(AppUser.country == country)
    new_users = users.where(AppUser.created_time >= start, AppUser.created_time < end).subquery()
    registrations = dict((await db.execute(
        select(new_users.c.package, func.count()).group_by(new_users.c.package)
    )).all())

    paid = paid_orders(start, end, package, country)
    revenue_rows = (await db.execute(
        select(
            paid.c.package, paid.c.currency, paid.c.channel, func.sum(paid.c.amount),
            func.sum(case((paid.c.is_new, paid.c.amount), else_=0)),
        ).where(paid.c.amount.is_not(None), paid.c.currency.is_not(None))
        .group_by(paid.c.package, paid.c.currency, paid.c.channel)
    )).all()
    currencies = sorted({code for _, code, *_ in revenue_rows if len(code) == 3 and code.isascii() and code.isalpha()})
    currency = currency or ("USD" if "USD" in currencies or not currencies else currencies[0])
    currency_options = sorted(set(currencies) | {"USD", currency})
    payer_rows = (await db.execute(
        select(
            paid.c.package, func.count(distinct(paid.c.user_id)),
            func.count(distinct(case((paid.c.is_new, paid.c.user_id)))), func.count(),
            func.count().filter(paid.c.amount.is_(None) | paid.c.currency.is_(None)),
            func.count(distinct(case(((paid.c.currency == currency) & paid.c.amount.is_not(None), paid.c.user_id)))),
        ).group_by(paid.c.package)
    )).all()
    payers = {row[0]: row[1:] for row in payer_rows}
    revenue = {}
    for key, code, channel, total, new in revenue_rows:
        if code == currency:
            revenue.setdefault(key, []).append({
                "name": channel, "total": round(float(total or 0), 2), "new": round(float(new or 0), 2),
            })

    has_activity = await db.scalar(select(
        select(DailyUserActivity.user_id).where(DailyUserActivity.stat_date == day).exists()
    ))
    active = {}
    legacy_dau = None
    if has_activity:
        tracked = users.join(DailyUserActivity, DailyUserActivity.user_id == AppUser.user_id).where(
            DailyUserActivity.stat_date == day
        )
        # Registration and successful payment also count as activity.
        active_users = union_all(
            tracked, select(new_users), select(paid.c.package, paid.c.user_id)
        ).subquery()
        active = dict((await db.execute(
            select(active_users.c.package, func.count(distinct(active_users.c.user_id)))
            .group_by(active_users.c.package)
        )).all())
    elif not package and not country:
        legacy_dau = await db.scalar(
            select(DailyStat.dau).where(DailyStat.stat_date == day.isoformat()).order_by(DailyStat.id.desc()).limit(1)
        )

    app_names = {app.package_name: app.app_name or app.package_name for app in apps if app.package_name}
    packages = set(registrations) | set(payers) | set(active)
    packages.update([package] if package else app_names)
    rows = []
    for key in sorted(packages, key=lambda key: (app_names.get(key, key).casefold(), key)):
        new_users_count = registrations.get(key, 0)
        dau = active.get(key, 0) if has_activity else None
        total_payers, new_payers, order_count, missing_prices, currency_payers = payers.get(key, (0, 0, 0, 0, 0))
        channels = sorted(revenue.get(key, []), key=lambda item: (-item["total"], item["name"]))
        total_income = round(sum(item["total"] for item in channels), 2)
        new_income = round(sum(item["new"] for item in channels), 2)
        rows.append({
            "package": key, "app_name": app_names.get(key, key),
            "new_users": new_users_count, "dau": dau,
            "total_payers": total_payers, "new_payers": new_payers, "orders": order_count,
            "total_income": total_income, "new_income": new_income, "channels": channels,
            "new_pay_rate": percentage(new_payers, new_users_count),
            "dau_pay_rate": percentage(total_payers, dau),
            "income_per_active": round(total_income / dau, 2) if dau else None,
            "income_per_payer": round(total_income / currency_payers, 2) if currency_payers else None,
            "missing_prices": missing_prices,
        })

    return templates.TemplateResponse(request, "dashboard.html", {
        "active_menu": "dashboard", "apps": app_names, "countries": countries, "country": country,
        "package": package, "day": day.isoformat(), "is_today": day == today,
        "currency": currency, "currency_options": currency_options, "rows": rows,
        "legacy_dau": legacy_dau, "has_activity": has_activity,
        "missing_prices": sum(row["missing_prices"] for row in rows),
    })
