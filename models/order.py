from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    order_no = Column(String(64), unique=True, nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default="pending", index=True)
    payment_method = Column(String(50))
    product_type = Column(String(50))
    product_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime)
    
    app = relationship("App", back_populates="orders")
    user = relationship("User", back_populates="orders")
    
    def to_dict(self):
        return {
            'id': self.id,
            'app_id': self.app_id,
            'user_id': self.user_id,
            'order_no': self.order_no,
            'amount': float(self.amount) if self.amount else 0,
            'status': self.status,
            'payment_method': self.payment_method,
            'product_type': self.product_type,
            'product_id': self.product_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
