from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from database import Base

class AppConfig(Base):
    __tablename__ = "app_configs"
    id = Column(Integer, primary_key=True)
    package_name = Column(String(100), ForeignKey("app_list.package_name"), index=True)
    app_version = Column(String(100), index=True)
    config_json = Column(String(2000))
    remark = Column(String(2000))

class AppReview(Base):
    __tablename__ = "app_review"
    id = Column(Integer, primary_key=True)
    package_name = Column(String(100), index=True)
    app_version = Column(String(16), index=True)