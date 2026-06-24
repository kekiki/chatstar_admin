from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta, date
from database import get_db
from models import App, User, Payment, Order, Activity, Streamer, Admin
import auth

dashboard_router = APIRouter()

@dashboard_router.get("/stats")
def get_stats(db: Session = Depends(get_db), current_admin: Admin = Depends(auth.get_current_admin)):
    total_apps = db.query(App).count()
    total_users = db.query(User).count()
    total_streamers = db.query(Streamer).count()
    total_orders = db.query(Order).count()
    total_revenue = db.query(func.sum(Payment.amount)).scalar() or 0
    
    return {
        "total_apps": total_apps,
        "total_users": total_users,
        "total_streamers": total_streamers,
        "total_orders": total_orders,
        "total_revenue": float(total_revenue)
    }

@dashboard_router.get("/apps")
def get_apps(db: Session = Depends(get_db), current_admin: Admin = Depends(auth.get_current_admin)):
    apps = db.query(App).filter(App.is_active == True).all()
    return {"apps": [app.to_dict() for app in apps]}

@dashboard_router.get("/app/{app_id}/stats")
def get_app_stats(app_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(auth.get_current_admin)):
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    # Date range for the last 30 days
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    # New users in the period
    new_users = db.query(User).filter(
        and_(
            User.app_id == app_id,
            User.created_at >= start_date,
            User.created_at <= end_date
        )
    ).count()
    
    # Total users
    total_users = db.query(User).filter(User.app_id == app_id).count()
    
    # New payments in the period
    new_payments = db.query(Payment).filter(
        and_(
            Payment.app_id == app_id,
            Payment.created_at >= start_date,
            Payment.created_at <= end_date
        )
    ).all()
    
    new_payment_amount = sum(p.amount for p in new_payments)
    new_payment_count = len(new_payments)
    
    # Total payments
    total_payments = db.query(Payment).filter(Payment.app_id == app_id).all()
    total_payment_amount = sum(p.amount for p in total_payments)
    
    # Daily active users (DAU)
    dau = db.query(Activity).filter(
        and_(
            Activity.app_id == app_id,
            Activity.activity_date == end_date
        )
    ).distinct(Activity.user_id).count()
    
    # Payment rates
    new_payment_rate = (new_payment_count / new_users * 100) if new_users > 0 else 0
    dau_payment_rate = (new_payment_count / dau * 100) if dau > 0 else 0
    
    # Daily data for charts
    daily_stats = []
    for i in range(30):
        day_date = end_date - timedelta(days=i)
        day_start = datetime.combine(day_date, datetime.min.time())
        day_end = datetime.combine(day_date, datetime.max.time())
        
        day_new_users = db.query(User).filter(
            and_(
                User.app_id == app_id,
                User.created_at >= day_start,
                User.created_at <= day_end
            )
        ).count()
        
        day_payments = db.query(Payment).filter(
            and_(
                Payment.app_id == app_id,
                Payment.created_at >= day_start,
                Payment.created_at <= day_end
            )
        ).all()
        
        day_payment_amount = sum(p.amount for p in day_payments)
        day_dau = db.query(Activity).filter(
            and_(
                Activity.app_id == app_id,
                Activity.activity_date == day_date
            )
        ).distinct(Activity.user_id).count()
        
        daily_stats.append({
            "date": day_date.isoformat(),
            "new_users": day_new_users,
            "new_payment_amount": float(day_payment_amount),
            "dau": day_dau
        })
    
    daily_stats.reverse()
    
    return {
        "app_id": app_id,
        "app_name": app.name,
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "summary": {
            "new_users": new_users,
            "total_users": total_users,
            "new_payment_amount": float(new_payment_amount),
            "total_payment_amount": float(total_payment_amount),
            "new_payment_count": new_payment_count,
            "dau": dau,
            "new_payment_rate": round(new_payment_rate, 2),
            "dau_payment_rate": round(dau_payment_rate, 2)
        },
        "daily_stats": daily_stats
    }
