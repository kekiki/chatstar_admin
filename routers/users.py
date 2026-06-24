from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import User, Admin
from schemas import UserUpdate
import auth

users_router = APIRouter()

@users_router.get("/")
def get_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    app_id: int = Query(None),
    is_active: bool = Query(None),
    is_premium: bool = Query(None),
    search: str = Query(None),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(auth.get_current_admin)
):
    query = db.query(User)
    
    if app_id:
        query = query.filter(User.app_id == app_id)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    if is_premium is not None:
        query = query.filter(User.is_premium == is_premium)
    
    if search:
        query = query.filter(
            or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.phone.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "users": [user.to_dict() for user in users],
        "total": total,
        "pages": (total + per_page - 1) // per_page,
        "current_page": page
    }

@users_router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(auth.get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user.to_dict()}

@users_router.put("/{user_id}")
def update_user(user_id: int, update_data: UserUpdate, db: Session = Depends(get_db), current_admin: Admin = Depends(auth.get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_dict = update_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return {"user": user.to_dict()}

@users_router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(auth.get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
