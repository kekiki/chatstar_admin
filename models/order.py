from sqlalchemy import Column, Integer, String
from database import Base

class PayOrder(Base):
    __tablename__ = "pay_orders"

    id = Column(Integer, primary_key=True, index=True)
    package_name = Column(String(100), index=True)
    user_id = Column(Integer, index=True)
    anchor_id = Column(Integer, index=True)
    transaction_no = Column(String, index=True)
    order_no = Column(String, index=True)
    created_time = Column(Integer, index=True)
    updated_time = Column(Integer, index=True)
    sku = Column(String, index=True)
    type = Column(Integer, default=0, index=True)# 0钻石 1首充 2VIP
    order_status = Column(Integer, default=0, index=True)# 0待支付 1支付成功 2支付失败 3已退款
    currency_code = Column(String, default="USD")
    currency_price = Column(Integer, default=0)
    pp_id = Column(Integer, default=1, index=True) #1 Google
    pp_type = Column(String, default="", index=True)
    path = Column(String, default="", index=True)
    agent = Column(String, default="", index=True)
    # Google Play 购买凭据，唯一索引防止同一笔购买在多个订单上重放
    purchase_token = Column(String, unique=True, index=True)
    google_order_id = Column(String, index=True)
