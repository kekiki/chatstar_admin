from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from database import Base

class PayOrder(Base):
    __tablename__ = "pay_order"
    id = Column(Integer, primary_key=True)
    app_id = Column(Integer, ForeignKey("app_config.id"))
    user_id = Column(Integer)
    pay_amount = Column(Float)
    pay_time = Column(DateTime)
    status = Column(Integer) # 0未支付 1已支付
