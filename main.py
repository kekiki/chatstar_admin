from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from database import get_db, engine, Base
import models
from routers import auth_router, dashboard_router, user_router, anchor_router, order_router, app_router

# 创建数据表（首次运行自动建表）
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ChatStar管理后台")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产替换为你的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(user_router)
app.include_router(anchor_router)
app.include_router(order_router)
app.include_router(app_router)

# 首页自动跳转看板
@app.get("/admin")
async def admin_index():
    return RedirectResponse("/admin/dashboard")

@app.get("/")
async def home():
    return RedirectResponse("/admin/dashboard")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)