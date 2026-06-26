from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import auth
from database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# 全局鉴权依赖，未登录跳转登录页
def require_login(request: Request, db: Session = Depends(get_db)):
    from typing import Optional
    token: Optional[str] = request.cookies.get("admin_token")
    if not token:
        raise HTTPException(status_code=302, headers={"location": "/login"})
    username = auth.get_current_admin(token)
    if not username:
        raise HTTPException(status_code=302, headers={"location": "/login"})
    return username

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    tpl = templates.env.get_template("login.html")
    content = tpl.render({"request": request})
    return HTMLResponse(content)

@router.post("/login")
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    import models
    admin = db.query(models.AdminUser).filter(models.AdminUser.username == username).first()
    if not admin or not auth.verify_password(password, admin.password):
        tpl = templates.env.get_template("login.html")
        content = tpl.render({"request": request, "msg": "账号密码错误"})
        return HTMLResponse(content)
    token = auth.create_access_token({"sub": username})
    resp = RedirectResponse(url="/admin/dashboard", status_code=302)
    resp.set_cookie(key="admin_token", value=token, httponly=True)
    return resp

@router.get("/logout")
async def logout():
    resp = RedirectResponse("/login")
    resp.delete_cookie("admin_token")
    return resp
