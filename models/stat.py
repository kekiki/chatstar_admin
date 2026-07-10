from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base

class DailyStat(Base):
    __tablename__ = "daily_stat"
    id = Column(Integer, primary_key=True)
    package_name = Column(String(100), ForeignKey("app_list.package_name"), index=True)
    stat_date = Column(String(20)) # yyyy-MM-dd
    new_user = Column(Integer, default=0) # 新增用户
    dau = Column(Integer, default=0) # 日活
    new_pay_user = Column(Integer, default=0) # 新增付费用户
    total_pay_money = Column(Float, default=0) # 总付费金额
