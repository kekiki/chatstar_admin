"""
Media database model.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database import Base
import datetime

class Media(Base):
    """Media model for SQLAlchemy ORM."""
    __tablename__ = "app_medias"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    cover = Column(String, default="")
    url = Column(String, default="")
    is_vip = Column(Boolean, default=False)
    is_video = Column(Boolean, default=False)
    created_time = Column(DateTime, default=lambda: datetime.datetime.now())
