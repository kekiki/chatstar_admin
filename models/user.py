from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False, index=True)
    username = Column(String(80), nullable=False, index=True)
    email = Column(String(120), index=True)
    phone = Column(String(20), index=True)
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    total_spent = Column(Numeric(10, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_active = Column(DateTime, index=True)
    
    app = relationship("App", back_populates="users")
    
    def to_dict(self):
        return {
            'id': self.id,
            'app_id': self.app_id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'is_active': self.is_active,
            'is_premium': self.is_premium,
            'total_spent': float(self.total_spent) if self.total_spent else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_active': self.last_active.isoformat() if self.last_active else None
        }
