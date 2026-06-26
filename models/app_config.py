from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from database import Base

class AppConfig(Base):
    __tablename__ = "app_config"
    id = Column(Integer, primary_key=True)
    app_id = Column(Integer, ForeignKey("app_list.id"))
    app_version = Column(String(100))
    config_json = Column(String(2000))
    remark = Column(String(2000))