from fastapi import FastAPI, Request, Depends, Form, HTTPException, Body, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from tools import get_page_params, paginate_query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import Optional
import auth
from database import get_db, engine
import models
import json
from fastapi.responses import StreamingResponse
import io

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

# 登录页面
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    tpl = templates.env.get_template("login.html")
    content = tpl.render({"request": request})
    return HTMLResponse(content)

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
        tpl = templates.env.get_template("login.html")
        content = tpl.render({"request": request, "msg": "账号密码错误"})
        return HTMLResponse(content)
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
    tpl = templates.env.get_template("dashboard.html")
    content = tpl.render({
        "request": request,
        "active_menu": "dashboard",
        "stat_list": stat_list,
        "app_list": app_list,
    })
    return HTMLResponse(content)

# @app.get("/admin/user", response_class=HTMLResponse)
# async def user_list(request: Request, db: Session = Depends(get_db), _user=Depends(require_login)):
#     user_list = db.query(models.AppUser).all()
#     tpl = templates.env.get_template("user_list.html")
#     content = tpl.render({"request": request, "active_menu": "user", "user_list": user_list})
#     return HTMLResponse(content)
@app.get("/admin/user", response_class=HTMLResponse)
async def user_list(
    request: Request,
    db: Session = Depends(get_db),
    page: int = Query(1),
    page_size: int = Query(10),
    keyword: str = Query("", description="全字段模糊搜索"),
    start_date: str = Query(""),
    end_date: str = Query(""),
    _user=Depends(require_login)
):
    page, page_size, offset = get_page_params(page, page_size)
    q = db.query(models.AppUser)

    # 全字段模糊匹配
    if keyword:
        q = q.filter(
            or_(
                models.AppUser.id.like(f"%{keyword}%"),
                models.AppUser.app_id.like(f"%{keyword}%"),
                models.AppUser.register_time.like(f"%{keyword}%"),
                models.AppUser.last_login.like(f"%{keyword}%")
            )
        )
    # 注册时间区间筛选
    if start_date:
        q = q.filter(models.AppUser.register_time >= start_date)
    if end_date:
        q = q.filter(models.AppUser.register_time <= f"{end_date} 23:59:59")

    page_data = paginate_query(db, q, offset, page_size)
    return templates.TemplateResponse("user_list.html", {
        "request": request,
        "active_menu": "user",
        "page_data": page_data,
        "keyword": keyword,
        "start_date": start_date,
        "end_date": end_date
    })

# @app.get("/admin/anchor", response_class=HTMLResponse)
# async def anchor_list(request: Request, db: Session = Depends(get_db), _user=Depends(require_login)):
#     anchor_list = db.query(models.Anchor).all()
#     tpl = templates.env.get_template("anchor_list.html")
#     content = tpl.render({"request": request, "active_menu": "anchor", "anchor_list": anchor_list})
#     return HTMLResponse(content)
@app.get("/admin/anchor", response_class=HTMLResponse)
async def anchor_list(
    request: Request,
    db: Session = Depends(get_db),
    page: int = Query(1),
    page_size: int = Query(10),
    keyword: str = Query("", description="全字段模糊搜索"),
    _user=Depends(require_login)
):
    page, page_size, offset = get_page_params(page, page_size)
    q = db.query(models.Anchor)

    if keyword:
        q = q.filter(
            or_(
                models.Anchor.id.like(f"%{keyword}%"),
                models.Anchor.user_id.like(f"%{keyword}%"),
                models.Anchor.nickname.like(f"%{keyword}%"),
                models.Anchor.income.like(f"%{keyword}%")
            )
        )

    page_data = paginate_query(db, q, offset, page_size)
    return templates.TemplateResponse("anchor_list.html", {
        "request": request,
        "active_menu": "anchor",
        "page_data": page_data,
        "keyword": keyword
    })

# @app.get("/admin/order", response_class=HTMLResponse)
# async def order_list(request: Request, db: Session = Depends(get_db), _user=Depends(require_login)):
#     order_list = db.query(models.PayOrder).all()
#     tpl = templates.env.get_template("order_list.html")
#     content = tpl.render({"request": request, "active_menu": "order", "order_list": order_list})
#     return HTMLResponse(content)
@app.get("/admin/order", response_class=HTMLResponse)
async def order_list(
    request: Request,
    db: Session = Depends(get_db),
    page: int = Query(1),
    page_size: int = Query(10),
    keyword: str = Query("", description="全字段模糊搜索"),
    start_date: str = Query(""),
    end_date: str = Query(""),
    status: int = Query(-1),
    _user=Depends(require_login)
):
    page, page_size, offset = get_page_params(page, page_size)
    q = db.query(models.PayOrder)

    # 全字段模糊
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
    # 支付时间区间
    if start_date:
        q = q.filter(models.PayOrder.pay_time >= start_date)
    if end_date:
        q = q.filter(models.PayOrder.pay_time <= f"{end_date} 23:59:59")
    # 订单状态
    if status in (0, 1):
        q = q.filter(models.PayOrder.status == status)

    page_data = paginate_query(db, q, offset, page_size)
    return templates.TemplateResponse("order_list.html", {
        "request": request,
        "active_menu": "order",
        "page_data": page_data,
        "keyword": keyword,
        "start_date": start_date,
        "end_date": end_date,
        "status": status
    })

@app.get("/admin/order/export")
async def export_order(
    db: Session = Depends(get_db),
    keyword: str = Query(""),
    start_date: str = Query(""),
    end_date: str = Query(""),
    status: int = Query(-1),
    _user=Depends(require_login)
):
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
    import io
    from fastapi.responses import StreamingResponse

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

@app.get("/admin/config", response_class=HTMLResponse)
async def app_config(request: Request, db: Session = Depends(get_db), _user=Depends(require_login)):
    apps = db.query(models.AppInfo).all()
    tpl = templates.env.get_template("app_config.html")
    content = tpl.render({"request": request, "active_menu": "config", "apps": apps})
    return HTMLResponse(content)

# 新增应用接口
@app.post("/admin/api/add_app")
async def add_app(
    app_name: str = Body(),
    app_key: str = Body(),
    config_json: str = Body(),
    db: Session = Depends(get_db),
    _user = Depends(require_login)
):
    exist = db.query(models.AppInfo).filter(models.AppInfo.app_key == app_key).first()
    if exist:
        return {"code": 400, "msg": "AppKey已存在"}
    new_app = models.AppInfo(
        app_name=app_name,
        app_key=app_key,
        config_json=config_json,
        status=True
    )
    db.add(new_app)
    db.commit()
    return {"code": 200, "msg": "新增成功"}

# 首页自动跳转看板
@app.get("/admin")
async def admin_index():
    return RedirectResponse("/admin/dashboard")

@app.get("/")
async def admin_index():
    return RedirectResponse("/admin/dashboard")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)