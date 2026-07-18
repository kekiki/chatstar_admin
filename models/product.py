"""
Product database model.
"""
from sqlalchemy import Column, Integer, String, Double
from database import Base


class Product(Base):
    """Product model for SQLAlchemy ORM."""
    __tablename__ = "app_products"
    
    id = Column(Integer, primary_key=True, index=True)
    package_name = Column(String(100), unique=True, index=True)
    sku = Column(String, unique=True)
    diamonds = Column(Integer, default=0)
    vip_days = Column(Integer, default=0)
    reward_diamonds = Column(Integer, default=0)
    discount_type = Column(Integer, default=0) # 0:普通商品，1:首充折扣
    discount = Column(Integer, default=100) # 折扣, 如75代表七五折
    currency_code = Column(String, default="USD")
    currency_price = Column(Double, default=0)
    call_card_num = Column(Integer, default=0)
    match_card_num = Column(Integer, default=0)
    chat_card_num = Column(Integer, default=0)
