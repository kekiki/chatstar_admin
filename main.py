from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from models import Admin, User, Streamer, Order, App

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ChatStar Admin API")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库查询接口 - 预留扩展点

@app.get("/api/apps")
def get_apps(db: Session = Depends(get_db)):
    """获取应用列表"""
    apps = db.query(App).all()
    return {"apps": [app.to_dict() for app in apps]}

@app.get("/api/users")
def get_users(
    page: int = 1,
    per_page: int = 20,
    search: str = None,
    app_id: int = None,
    is_active: bool = None,
    is_premium: bool = None,
    db: Session = Depends(get_db)
):
    """获取用户列表 - 支持筛选"""
    query = db.query(User)
    
    if search:
        query = query.filter(
            (User.username.contains(search)) |
            (User.email.contains(search)) |
            (User.phone.contains(search))
        )
    if app_id:
        query = query.filter(User.app_id == app_id)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if is_premium is not None:
        query = query.filter(User.is_premium == is_premium)
    
    total = query.count()
    users = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "users": [user.to_dict() for user in users],
        "total": total
    }

@app.get("/api/streamers")
def get_streamers(
    page: int = 1,
    per_page: int = 20,
    search: str = None,
    app_id: int = None,
    is_active: bool = None,
    is_verified: bool = None,
    db: Session = Depends(get_db)
):
    """获取主播列表 - 支持筛选"""
    query = db.query(Streamer)
    
    if search:
        query = query.filter(
            (Streamer.username.contains(search)) |
            (Streamer.display_name.contains(search))
        )
    if app_id:
        query = query.filter(Streamer.app_id == app_id)
    if is_active is not None:
        query = query.filter(Streamer.is_active == is_active)
    if is_verified is not None:
        query = query.filter(Streamer.is_verified == is_verified)
    
    total = query.count()
    streamers = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "streamers": [streamer.to_dict() for streamer in streamers],
        "total": total
    }

@app.get("/api/orders")
def get_orders(
    page: int = 1,
    per_page: int = 20,
    search: str = None,
    app_id: int = None,
    user_id: int = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    """获取订单列表 - 支持筛选"""
    query = db.query(Order)
    
    if search:
        query = query.filter(Order.order_no.contains(search))
    if app_id:
        query = query.filter(Order.app_id == app_id)
    if user_id:
        query = query.filter(Order.user_id == user_id)
    if status:
        query = query.filter(Order.status == status)
    
    total = query.count()
    orders = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "orders": [order.to_dict() for order in orders],
        "total": total
    }

@app.get("/api/dashboard/apps")
def get_dashboard_apps(db: Session = Depends(get_db)):
    """获取看板应用列表"""
    apps = db.query(App).filter(App.is_active == True).all()
    return {"apps": [app.to_dict() for app in apps]}

@app.get("/api/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """获取总体统计"""
    total_apps = db.query(App).count()
    total_users = db.query(User).count()
    total_streamers = db.query(Streamer).count()
    total_orders = db.query(Order).count()
    
    return {
        "total_apps": total_apps,
        "total_users": total_users,
        "total_streamers": total_streamers,
        "total_orders": total_orders,
        "total_revenue": sum([float(o.amount) for o in db.query(Order).all()]) or 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
