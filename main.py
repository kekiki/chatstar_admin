from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, get_db
from models import Base
import auth
import routers

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ChatStar Admin API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routers.auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(routers.dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(routers.users_router, prefix="/api/users", tags=["Users"])
app.include_router(routers.streamers_router, prefix="/api/streamers", tags=["Streamers"])
app.include_router(routers.orders_router, prefix="/api/orders", tags=["Orders"])
app.include_router(routers.apps_router, prefix="/api/apps", tags=["Apps"])

@app.get("/")
def root():
    return {"message": "ChatStar Admin API", "status": "running"}

@app.get("/api/health")
def health():
    return {"status": "ok"}
