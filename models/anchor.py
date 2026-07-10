from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database import Base
import datetime

class Anchor(Base):
    __tablename__ = "app_anchors"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    created_time = Column(DateTime, default=lambda: datetime.datetime.now())
    country = Column(String(64), default="US")
    nickname = Column(String(100))
    avatar = Column(String)
    age = Column(Integer, default=20)
    language_name = Column(String(64), default="English")
    language_code = Column(String(16), default="en")
    follow_count = Column(Integer, default=0)
    fans_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    is_review = Column(Boolean, default=False)
