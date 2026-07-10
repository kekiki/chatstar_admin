from sqlalchemy import Column, Integer, String
from database import Base

class PayOrder(Base):
    __tablename__ = "pay_orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    order_no = Column(String, index=True)
    created_time = Column(Integer)
    sku = Column(String)
    discount_type = Column(Integer, default=0) # 0普通折扣 1首充折扣
    order_status = Column(Integer, default=0) # 0待支付 1支付成功 2支付失败
    currency_code = Column(String, default="USD")
    currency_price = Column(Integer, default=0)
