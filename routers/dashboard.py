from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
import models

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db), _user=Depends(lambda: None)):
    from routers.auth import require_login
    _user = require_login(request, db)
    stat_list = db.query(models.DailyStat).order_by(models.DailyStat.stat_date).all()
    app_list = db.query(models.AppInfo).all()
    tpl = templates.env.get_template("dashboard.html")
    content = tpl.render({
        "request": request,
        "active_menu": "dashboard",
        "stat_list": stat_list,
        "app_list": app_list,
    })
    return HTMLResponse(content)
