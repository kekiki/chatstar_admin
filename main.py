from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
import auth
from database import get_db, engine
import models

# 创建数据表（首次运行自动建表）
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ChatStar管理后台")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 生产替换为你的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
# app.mount("/static", StaticFiles(directory="static"), name="static")
# 模板目录
templates = Jinja2Templates(directory="templates")
# Disable Jinja2 template caching to avoid environment cache key issues in some Jinja2 versions
# (container should instead install the pinned `jinja2==3.0.3` from requirements.txt)
templates.env.cache = None

# 全局鉴权依赖，未登录跳转登录页
def require_login(request: Request, db: Session = Depends(get_db)):
    token: Optional[str] = request.cookies.get("admin_token")
    if not token:
        raise HTTPException(status_code=302, headers={"location": "/login"})
    username = auth.get_current_admin(token)
    if not username:
        raise HTTPException(status_code=302, headers={"location": "/login"})
    return username

@app.get("/")
def home():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "chatstar-api",
        "version": "1.0.0"
    }

# 登录页面
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# 登录提交接口
@app.post("/login")
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    admin = db.query(models.AdminUser).filter(models.AdminUser.username == username).first()
    if not admin or not auth.verify_password(password, admin.password):
        return templates.TemplateResponse("login.html", {"request": request, "msg": "账号密码错误"})
    # 生成token写入cookie
    token = auth.create_access_token({"sub": username})
    resp = RedirectResponse(url="/admin/dashboard", status_code=302)
    resp.set_cookie(key="admin_token", value=token, httponly=True)
    return resp

# 退出登录
@app.get("/logout")
async def logout():
    resp = RedirectResponse("/login")
    resp.delete_cookie("admin_token")
    return resp

# ---------------- 后台路由（全部需要登录） ----------------
@app.get("/admin/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db), _user=Depends(require_login)):
    # 查询统计数据给ECharts渲染
    stat_list = db.query(models.DailyStat).order_by(models.DailyStat.stat_date).all()
    app_list = db.query(models.AppInfo).all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "active_menu": "dashboard",
        "stat_list": stat_list,
        "app_list": app_list
    })

@app.get("/admin/user", response_class=HTMLResponse)
async def user_list(request: Request, db: Session = Depends(get_db), _user=Depends(require_login)):
    user_list = db.query(models.AppUser).all()
    return templates.TemplateResponse("user_list.html", {"request": request, "active_menu": "user", "user_list": user_list})

@app.get("/admin/anchor", response_class=HTMLResponse)
async def anchor_list(request: Request, db: Session = Depends(get_db), _user=Depends(require_login)):
    anchor_list = db.query(models.Anchor).all()
    return templates.TemplateResponse("anchor_list.html", {"request": request, "active_menu": "anchor", "anchor_list": anchor_list})

@app.get("/admin/order", response_class=HTMLResponse)
async def order_list(request: Request, db: Session = Depends(get_db), _user=Depends(require_login)):
    order_list = db.query(models.PayOrder).all()
    return templates.TemplateResponse("order_list.html", {"request": request, "active_menu": "order", "order_list": order_list})

@app.get("/admin/config", response_class=HTMLResponse)
async def app_config(request: Request, db: Session = Depends(get_db), _user=Depends(require_login)):
    apps = db.query(models.AppInfo).all()
    return templates.TemplateResponse("app_config.html", {"request": request, "active_menu": "config", "apps": apps})

# 首页自动跳转看板
@app.get("/admin")
async def admin_index():
    return RedirectResponse("/admin/dashboard")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)