from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_type = Column(String(20), default="new")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    app = relationship("App", back_populates="payments")
    user = relationship("User", back_populates="payments")
    order = relationship("Order", back_populates="payments")
    
    def to_dict(self):
        return {
            'id': self.id,
            'app_id': self.app_id,
            'user_id': self.user_id,
            'order_id': self.order_id,
            'amount': float(self.amount) if self.amount else 0,
            'payment_type': self.payment_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
