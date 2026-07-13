from sqlalchemy import Column, Integer, ForeignKey, Boolean, String
from database import Base
import datetime

class AppUser(Base):
    __tablename__ = "app_users"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    device_id = Column(String(64), index=True)
    package_name = Column(String(100), ForeignKey("app_list.package_name"), index=True)
    created_time = Column(Integer, default=lambda: int(datetime.datetime.now().timestamp()))
    country = Column(String(64), default="US")
    ip = Column(String(64))
    nickname = Column(String(64))
    avatar = Column(String)
    email = Column(String(128), index=True)
    google_id = Column(String(128), index=True)
    balance = Column(Integer, default=0)
    vip_expire_time = Column(Integer)
    language_name = Column(String(64), default="English")
    language_code = Column(String(16), default="en")
    is_review = Column(Boolean, default=False)
    agent = Column(String(255), default="")
    birthday = Column(Integer, default=lambda: int(datetime.datetime.now().timestamp() - 86400 * 365 * 25))

    # Review flag
    is_review = Column(Boolean, default=False)

    # Install referrer tracking
    install_referrer = Column(String(255))
    referrer_click_timestamp_seconds = Column(Integer)
    install_begin_timestamp_seconds = Column(Integer)
    referrer_click_timestamp_server_seconds = Column(Integer)
    install_begin_timestamp_server_seconds = Column(Integer)
    install_version = Column(String(64))
    google_play_instant = Column(Boolean, default=False)
    password = Column(String(255))

