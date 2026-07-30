from sqlalchemy import Column, Integer, String
from database import Base

class Gift(Base):
    __tablename__ = "app_gifts"
    id = Column(Integer, primary_key=True)
    gift_name = Column(String(100))
    gift_icon = Column(String(255))
    gift_price = Column(Integer)
    gift_animation = Column(String(255))