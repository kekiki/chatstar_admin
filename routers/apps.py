from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import secrets
from database import get_db
from models import App, Admin
from schemas import AppCreate, AppUpdate
import auth

apps_router = APIRouter()

@apps_router.get("/")
def get_apps(db: Session = Depends(get_db), current_admin: Admin = Depends(auth.get_current_admin)):
    apps = db.query(App).all()
    return {"apps": [app.to_dict() for app in apps]}

@apps_router.post("/")
def create_app(app_data: AppCreate, db: Session = Depends(get_db), current_admin: Admin = Depends(auth.get_current_admin)):
    # Check if app name already exists
    existing = db.query(App).filter(App.name == app_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="App name already exists")
    
    # Generate unique app key
    app_key = secrets.token_urlsafe(32)
    
    app = App(
        name=app_data.name,
        app_key=app_key,
        description=app_data.description,
        icon_url=app_data.icon_url,
        config=app_data.config
    )
    
    db.add(app)
    db.commit()
    db.refresh(app)
    
    return {"app": app.to_dict()}

@apps_router.get("/{app_id}")
def get_app(app_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(auth.get_current_admin)):
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    return {"app": app.to_dict()}

@apps_router.put("/{app_id}")
def update_app(app_id: int, update_data: AppUpdate, db: Session = Depends(get_db), current_admin: Admin = Depends(auth.get_current_admin)):
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    update_dict = update_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(app, key, value)
    
    app.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(app)
    
    return {"app": app.to_dict()}

@apps_router.delete("/{app_id}")
def delete_app(app_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(auth.get_current_admin)):
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    db.delete(app)
    db.commit()
    return {"message": "App deleted successfully"}

@apps_router.post("/{app_id}/regenerate-key")
def regenerate_app_key(app_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(auth.get_current_admin)):
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    app.app_key = secrets.token_urlsafe(32)
    app.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(app)
    
    return {"app": app.to_dict()}
