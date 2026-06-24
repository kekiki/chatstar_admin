from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class AdminResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: Optional[str] = None
    last_login: Optional[str] = None

class UserCreate(BaseModel):
    app_id: int
    username: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    is_active: bool = True
    is_premium: bool = False

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    is_premium: Optional[bool] = None

class StreamerCreate(BaseModel):
    app_id: int
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False

class StreamerUpdate(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

class OrderUpdate(BaseModel):
    status: str

class AppCreate(BaseModel):
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    config: Optional[dict] = None

class AppUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None
    is_active: Optional[bool] = None
    config: Optional[dict] = None
