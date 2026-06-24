from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Numeric, DateTime, ForeignKey
from database import Base

class Streamer(Base):
    __tablename__ = "streamers"
    
    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey('apps.id'), nullable=False, index=True)
    username = Column(String(80), nullable=False, index=True)
    display_name = Column(String(100))
    avatar_url = Column(String(500))
    bio = Column(String(500))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    follower_count = Column(Integer, default=0)
    total_earnings = Column(Numeric(10, 2), default=0.00)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_stream = Column(DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'app_id': self.app_id,
            'username': self.username,
            'display_name': self.display_name,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'follower_count': self.follower_count,
            'total_earnings': float(self.total_earnings) if self.total_earnings else 0.00,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_stream': self.last_stream.isoformat() if self.last_stream else None
        }
