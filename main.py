from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from config import APP_TITLE, APP_HOST, APP_PORT
from routers import auth_router, dashboard_router, user_router, anchor_router, order_router, app_list_router, app_review_router, media_router

app = FastAPI(title=APP_TITLE)
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
app.include_router(app_list_router)
app.include_router(app_review_router)
app.include_router(media_router)

# 首页自动跳转看板
@app.get("/admin")
async def admin_index():
    return RedirectResponse("/admin/dashboard")

@app.get("/")
async def home():
    return RedirectResponse("/admin/dashboard")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=APP_HOST, port=APP_PORT, reload=True)