from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from database import Base
import datetime

# 管理员账号表
class AdminUser(Base):
    __tablename__ = "admin_user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(200))
    create_time = Column(DateTime, default=datetime.datetime.now)

# APP应用列表
class AppList(Base):
    __tablename__ = "app_list"
    id = Column(Integer, primary_key=True)
    app_name = Column(String(100))
    bound_id = Column(String(100), unique=True)
    is_online = Column(Boolean, default=True)

# APP应用配置
class AppInfo(Base):
    __tablename__ = "app_info"
    id = Column(Integer, primary_key=True)
    app_id = Column(Integer, ForeignKey("app_list.id"))
    app_name = Column(String(100))
    app_key = Column(String(100), unique=True)
    status = Column(Boolean, default=True)
    config_json = Column(String(2000))

# 用户表
class AppUser(Base):
    __tablename__ = "app_user"
    id = Column(Integer, primary_key=True)
    app_id = Column(Integer, ForeignKey("app_list.id"))
    register_time = Column(DateTime)
    last_login = Column(DateTime)
    is_anchor = Column(Boolean, default=False)

# 主播表
class Anchor(Base):
    __tablename__ = "anchor"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("app_user.id"))
    nickname = Column(String(100))
    income = Column(Float, default=0)

# 订单付费表
class PayOrder(Base):
    __tablename__ = "pay_order"
    id = Column(Integer, primary_key=True)
    app_id = Column(Integer, ForeignKey("app_info.id"))
    user_id = Column(Integer)
    pay_amount = Column(Float)
    pay_time = Column(DateTime)
    status = Column(Integer) # 0未支付 1已支付

# 日统计数据表（看板数据源）
class DailyStat(Base):
    __tablename__ = "daily_stat"
    id = Column(Integer, primary_key=True)
    app_id = Column(Integer)
    stat_date = Column(String(20)) # yyyy-MM-dd
    new_user = Column(Integer, default=0) # 新增用户
    dau = Column(Integer, default=0) # 日活
    new_pay_user = Column(Integer, default=0) # 新增付费用户
    total_pay_money = Column(Float, default=0) # 总付费金额