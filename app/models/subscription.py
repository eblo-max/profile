"""Subscription model"""

from datetime import datetime, timedelta
from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey, 
    Boolean, DateTime, Enum as SQLAEnum, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel
from app.utils.constants import SubscriptionType, PaymentStatus


class Subscription(BaseModel):
    """Subscription model"""
    
    __tablename__ = "subscriptions"
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Subscription details
    subscription_type = Column(SQLAEnum(SubscriptionType), nullable=False)
    price = Column(Float, nullable=False)  # Price paid
    currency = Column(String(3), default="RUB")
    
    # Duration
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=False)
    duration_days = Column(Integer, nullable=False)  # Subscription duration
    
    # Payment details
    payment_id = Column(String(255), nullable=True)  # External payment ID
    payment_method = Column(String(50), nullable=True)  # Payment method used
    payment_status = Column(SQLAEnum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_date = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=False)
    is_cancelled = Column(Boolean, default=False)
    is_refunded = Column(Boolean, default=False)
    auto_renewal = Column(Boolean, default=False)
    
    # Metadata
    purchase_source = Column(String(50), nullable=True)  # Where subscription was purchased
    referral_code = Column(String(50), nullable=True)  # Referral code used
    promo_code = Column(String(50), nullable=True)  # Promo code used
    discount_amount = Column(Float, default=0.0)  # Discount applied
    
    # Additional info
    notes = Column(Text, nullable=True)  # Admin notes
    cancellation_reason = Column(String(255), nullable=True)
    refund_reason = Column(String(255), nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="subscriptions")
    
    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, user_id={self.user_id}, type={self.subscription_type})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if subscription is expired"""
        return datetime.utcnow() > self.end_date
    
    @property
    def days_remaining(self) -> int:
        """Get days remaining in subscription"""
        if self.is_expired:
            return 0
        return (self.end_date - datetime.utcnow()).days
    
    @property
    def is_expiring_soon(self) -> bool:
        """Check if subscription expires within 3 days"""
        return self.days_remaining <= 3 and self.days_remaining > 0
    
    @property
    def progress_percentage(self) -> float:
        """Get subscription progress as percentage"""
        total_duration = (self.end_date - self.start_date).days
        elapsed = (datetime.utcnow() - self.start_date).days
        
        if total_duration <= 0:
            return 100.0
        
        progress = min(100.0, max(0.0, (elapsed / total_duration) * 100))
        return round(progress, 1)
    
    @property
    def status_text(self) -> str:
        """Get human-readable status"""
        if self.is_refunded:
            return "Возвращен"
        elif self.is_cancelled:
            return "Отменен"
        elif self.is_expired:
            return "Истек"
        elif self.is_expiring_soon:
            return f"Истекает через {self.days_remaining} дн."
        elif self.is_active:
            return "Активен"
        else:
            return "Неактивен"
    
    def activate(self) -> None:
        """Activate subscription"""
        self.is_active = True
        self.payment_status = PaymentStatus.COMPLETED
        self.payment_date = datetime.utcnow()
    
    def cancel(self, reason: str = None) -> None:
        """Cancel subscription"""
        self.is_cancelled = True
        self.is_active = False
        self.auto_renewal = False
        if reason:
            self.cancellation_reason = reason
    
    def refund(self, reason: str = None) -> None:
        """Process refund"""
        self.is_refunded = True
        self.is_active = False
        self.is_cancelled = True
        self.payment_status = PaymentStatus.REFUNDED
        if reason:
            self.refund_reason = reason
    
    def extend(self, days: int) -> None:
        """Extend subscription by given days"""
        self.end_date += timedelta(days=days)
        self.duration_days += days
    
    def get_summary(self) -> dict:
        """Get subscription summary"""
        return {
            "id": self.id,
            "subscription_type": self.subscription_type.value,
            "price": self.price,
            "currency": self.currency,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "days_remaining": self.days_remaining,
            "is_active": self.is_active,
            "is_expired": self.is_expired,
            "status_text": self.status_text,
            "progress_percentage": self.progress_percentage
        }
    
    @classmethod
    def create_subscription(
        cls,
        user_id: int,
        subscription_type: SubscriptionType,
        price: float,
        duration_days: int = 30
    ) -> "Subscription":
        """Create new subscription"""
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=duration_days)
        
        return cls(
            user_id=user_id,
            subscription_type=subscription_type,
            price=price,
            start_date=start_date,
            end_date=end_date,
            duration_days=duration_days
        ) 