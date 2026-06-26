from sqlalchemy import Column, Integer, String, DateTime
from database import Base
import datetime

class AdminUser(Base):
    __tablename__ = "admin_user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(200))
    create_time = Column(DateTime, default=datetime.datetime.now)
