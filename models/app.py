from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from database import Base

class App(Base):
    __tablename__ = "apps"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    app_key = Column(String(64), unique=True, nullable=False, index=True)
    description = Column(String(500))
    icon_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    config = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    users = relationship("User", back_populates="app")
    streamers = relationship("Streamer", back_populates="app")
    orders = relationship("Order", back_populates="app")
    payments = relationship("Payment", back_populates="app")
    activities = relationship("Activity", back_populates="app")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'app_key': self.app_key,
            'description': self.description,
            'icon_url': self.icon_url,
            'is_active': self.is_active,
            'config': self.config,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
