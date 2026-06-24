from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import Streamer, Admin
from schemas import StreamerUpdate
import auth

streamers_router = APIRouter()

@streamers_router.get("/")
def get_streamers(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    app_id: int = Query(None),
    is_active: bool = Query(None),
    is_verified: bool = Query(None),
    search: str = Query(None),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(auth.get_current_admin)
):
    query = db.query(Streamer)
    
    if app_id:
        query = query.filter(Streamer.app_id == app_id)
    
    if is_active is not None:
        query = query.filter(Streamer.is_active == is_active)
    
    if is_verified is not None:
        query = query.filter(Streamer.is_verified == is_verified)
    
    if search:
        query = query.filter(
            or_(
                Streamer.username.ilike(f"%{search}%"),
                Streamer.display_name.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    streamers = query.order_by(Streamer.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "streamers": [streamer.to_dict() for streamer in streamers],
        "total": total,
        "pages": (total + per_page - 1) // per_page,
        "current_page": page
    }

@streamers_router.get("/{streamer_id}")
def get_streamer(streamer_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(auth.get_current_admin)):
    streamer = db.query(Streamer).filter(Streamer.id == streamer_id).first()
    if not streamer:
        raise HTTPException(status_code=404, detail="Streamer not found")
    return {"streamer": streamer.to_dict()}

@streamers_router.put("/{streamer_id}")
def update_streamer(streamer_id: int, update_data: StreamerUpdate, db: Session = Depends(get_db), current_admin: Admin = Depends(auth.get_current_admin)):
    streamer = db.query(Streamer).filter(Streamer.id == streamer_id).first()
    if not streamer:
        raise HTTPException(status_code=404, detail="Streamer not found")
    
    update_dict = update_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(streamer, key, value)
    
    db.commit()
    db.refresh(streamer)
    return {"streamer": streamer.to_dict()}

@streamers_router.delete("/{streamer_id}")
def delete_streamer(streamer_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(auth.get_current_admin)):
    streamer = db.query(Streamer).filter(Streamer.id == streamer_id).first()
    if not streamer:
        raise HTTPException(status_code=404, detail="Streamer not found")
    
    db.delete(streamer)
    db.commit()
    return {"message": "Streamer deleted successfully"}
