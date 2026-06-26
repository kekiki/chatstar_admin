from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean
from database import Base

class AppUser(Base):
    __tablename__ = "app_user"
    id = Column(Integer, primary_key=True)
    app_id = Column(Integer, ForeignKey("app_list.id"))
    register_time = Column(DateTime)
    last_login = Column(DateTime)
    is_anchor = Column(Boolean, default=False)
