"""User model for database"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column, Integer, BigInteger, String, Boolean, 
    DateTime, Enum as SQLAEnum, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel
from app.utils.enums import SubscriptionType


class User(BaseModel):
    """User model"""
    
    __tablename__ = "users"
    
    # Telegram data
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(10), default="ru")
    
    # Profile data
    name = Column(String(255), nullable=True)
    gender = Column(String(20), nullable=True)  # male, female, other
    age_group = Column(String(50), nullable=True)  # 18-25, 26-35, etc.
    interests = Column(Text, nullable=True)  # JSON array as text
    goals = Column(Text, nullable=True)  # JSON array as text
    bio = Column(Text, nullable=True)
    personality_type = Column(String(100), nullable=True)
    subscription_type = Column(
        SQLAEnum(SubscriptionType, validate_strings=True, create_constraint=True),
        default=SubscriptionType.FREE,
        nullable=False
    )
    
    # Usage statistics
    analyses_count = Column(Integer, default=0)
    analyses_limit = Column(Integer, default=3)  # Free tier limit
    total_analyses = Column(Integer, default=0)
    
    # Timestamps
    registration_date = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    last_analysis_date = Column(DateTime(timezone=True), nullable=True)
    last_profile_edit = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_new_user = Column(Boolean, default=True)
    
    # Settings
    notifications_enabled = Column(Boolean, default=True)
    daily_tips_enabled = Column(Boolean, default=True)
    analysis_reminders_enabled = Column(Boolean, default=True)
    weekly_stats_enabled = Column(Boolean, default=False)
    notification_time = Column(String(5), default="09:00")  # HH:MM format
    timezone = Column(String(50), default="Europe/Moscow")
    
    # Additional data
    referral_code = Column(String(50), nullable=True, unique=True)
    referred_by = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)  # Admin notes
    
    # Relationships
    analyses = relationship("TextAnalysis", back_populates="user", cascade="all, delete-orphan")
    partner_profiles = relationship("PartnerProfile", back_populates="user", cascade="all, delete-orphan")
    compatibility_tests = relationship("CompatibilityTest", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("UserActivity", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, name={self.first_name})>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or "Пользователь"
    
    @property
    def display_name(self) -> str:
        """Get user's display name"""
        return self.name or self.full_name
    
    @property
    def interests_list(self) -> list:
        """Get interests as list"""
        if not self.interests:
            return []
        try:
            import json
            return json.loads(self.interests)
        except:
            return []
    
    @property
    def goals_list(self) -> list:
        """Get goals as list"""
        if not self.goals:
            return []
        try:
            import json
            return json.loads(self.goals)
        except:
            return []
    
    @property
    def is_premium(self) -> bool:
        """Check if user has premium subscription"""
        return self.subscription_type in ["PREMIUM", "VIP"]
    
    @property
    def is_vip(self) -> bool:
        """Check if user has VIP subscription"""
        return self.subscription_type == "VIP"
    
    @property
    def can_analyze(self) -> bool:
        """Check if user can perform analysis"""
        if self.is_premium:
            return True
        return self.analyses_count < self.analyses_limit
    
    @property
    def analyses_remaining(self) -> int:
        """Get remaining analyses for free users"""
        if self.is_premium:
            return 999  # Unlimited
        return max(0, self.analyses_limit - self.analyses_count)
    
    def increment_analysis_count(self) -> None:
        """Increment analysis count"""
        self.analyses_count += 1
        self.total_analyses += 1
        self.last_analysis_date = datetime.utcnow()
    
    def reset_monthly_limit(self) -> None:
        """Reset monthly analysis limit (for free users)"""
        if not self.is_premium:
            self.analyses_count = 0
    
    def update_activity(self) -> None:
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow() 
    
    @property
    def can_edit_profile(self) -> bool:
        """Check if user can edit profile (once per month)"""
        if not self.last_profile_edit:
            return True
        
        # Calculate time difference
        now = datetime.utcnow()
        time_diff = now - self.last_profile_edit
        
        # Allow editing if more than 30 days have passed
        return time_diff.days >= 30
    
    @property
    def days_until_next_edit(self) -> int:
        """Get days until next profile edit is allowed"""
        if not self.last_profile_edit:
            return 0
        
        now = datetime.utcnow()
        time_diff = now - self.last_profile_edit
        days_passed = time_diff.days
        
        return max(0, 30 - days_passed)
    
    def update_profile_edit_time(self) -> None:
        """Update last profile edit timestamp"""
        self.last_profile_edit = datetime.utcnow() 