from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import Order, Payment, Admin
from schemas import OrderUpdate
import auth

orders_router = APIRouter()

@orders_router.get("/")
def get_orders(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    app_id: int = Query(None),
    user_id: int = Query(None),
    status: str = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(auth.get_current_admin)
):
    query = db.query(Order)
    
    if app_id:
        query = query.filter(Order.app_id == app_id)
    
    if user_id:
        query = query.filter(Order.user_id == user_id)
    
    if status:
        query = query.filter(Order.status == status)
    
    if start_date:
        start_datetime = datetime.fromisoformat(start_date)
        query = query.filter(Order.created_at >= start_datetime)
    
    if end_date:
        end_datetime = datetime.fromisoformat(end_date)
        query = query.filter(Order.created_at <= end_datetime)
    
    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "orders": [order.to_dict() for order in orders],
        "total": total,
        "pages": (total + per_page - 1) // per_page,
        "current_page": page
    }

@orders_router.get("/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(auth.get_current_admin)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"order": order.to_dict()}

@orders_router.put("/{order_id}")
def update_order(order_id: int, update_data: OrderUpdate, db: Session = Depends(get_db), current_admin: Admin = Depends(auth.get_current_admin)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = update_data.status
    if update_data.status == "completed" and not order.completed_at:
        order.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    return {"order": order.to_dict()}

@orders_router.get("/stats/summary")
def get_order_stats(
    app_id: int = Query(None),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(auth.get_current_admin)
):
    query = db.query(Order)
    if app_id:
        query = query.filter(Order.app_id == app_id)
    
    total_orders = query.count()
    completed_orders = query.filter(Order.status == "completed").count()
    pending_orders = query.filter(Order.status == "pending").count()
    cancelled_orders = query.filter(Order.status == "cancelled").count()
    refunded_orders = query.filter(Order.status == "refunded").count()
    
    # Revenue from completed orders
    payment_query = db.query(Payment)
    if app_id:
        payment_query = payment_query.filter(Payment.app_id == app_id)
    
    total_revenue = sum(p.amount for p in payment_query.all())
    
    return {
        "total_orders": total_orders,
        "completed_orders": completed_orders,
        "pending_orders": pending_orders,
        "cancelled_orders": cancelled_orders,
        "refunded_orders": refunded_orders,
        "total_revenue": float(total_revenue)
    }
