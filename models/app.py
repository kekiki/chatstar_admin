from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from database import Base

class AppList(Base):
    __tablename__ = "app_list"
    id = Column(Integer, primary_key=True)
    app_name = Column(String(100))
    bound_id = Column(String(100))
    is_online = Column(Boolean, default=True)

class AppInfo(Base):
    __tablename__ = "app_info"
    id = Column(Integer, primary_key=True)
    app_id = Column(Integer, ForeignKey("app_list.id"))
    app_name = Column(String(100))
    app_key = Column(String(100), unique=True)
    status = Column(Boolean, default=True)
    config_json = Column(String(2000))
