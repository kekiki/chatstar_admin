from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
import models

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: AsyncSession = Depends(get_db), _user=Depends(lambda: None)):
    from routers.auth import require_login
    _user = require_login(request, db)
    stat_stmt = select(models.DailyStat).order_by(models.DailyStat.stat_date)
    stat_result = await db.execute(stat_stmt)
    stat_list = stat_result.scalars().all()

    app_stmt = select(models.AppList)
    app_result = await db.execute(app_stmt)
    app_list = app_result.scalars().all()

    tpl = templates.env.get_template("dashboard.html")
    content = tpl.render({
        "request": request,
        "active_menu": "dashboard",
        "stat_list": stat_list,
        "app_list": app_list,
    })
    return HTMLResponse(content)
