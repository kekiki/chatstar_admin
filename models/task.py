from sqlalchemy import Column, Integer, String
from database import Base

class Task(Base):
    __tablename__ = "app_tasks"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    desc = Column(String(255))
    icon = Column(String(255))
    num = Column(Integer, default=0)
    category = Column(Integer, default=0)
    type = Column(String(50), default="")
    reward_diamonds = Column(Integer, default=0)
    call_card_num = Column(Integer, default=0)
    match_card_num = Column(Integer, default=0)
    chat_card_num = Column(Integer, default=0)
    sort = Column(Integer, default=0)
    status = Column(Integer, default=1)  # 0:下架 1:上架

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "desc": self.desc,
            "icon": self.icon,
            "num": self.num,
            "type": self.type,
            "reward_diamonds": self.reward_diamonds,
            "call_card_num": self.call_card_num,
            "match_card_num": self.match_card_num,
            "chat_card_num": self.chat_card_num,
            "sort": self.sort,
            "status": self.status,
        }