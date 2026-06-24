from datetime import datetime, date
from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    activity_date = Column(Date, nullable=False, index=True)
    session_count = Column(Integer, default=0)
    duration_seconds = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    app = relationship("App", back_populates="activities")
    user = relationship("User", back_populates="activities")
    
    def to_dict(self):
        return {
            'id': self.id,
            'app_id': self.app_id,
            'user_id': self.user_id,
            'activity_date': self.activity_date.isoformat() if self.activity_date else None,
            'session_count': self.session_count,
            'duration_seconds': self.duration_seconds,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
