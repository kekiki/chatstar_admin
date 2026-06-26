from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base

class Anchor(Base):
    __tablename__ = "anchor"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("app_user.id"))
    nickname = Column(String(100))
    income = Column(Float, default=0)
