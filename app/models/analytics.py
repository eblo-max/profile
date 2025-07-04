"""Analytics and user activity models"""

from sqlalchemy import (
    Column, Integer, String, Text, Float, ForeignKey, 
    Boolean, JSON, Enum as SQLAEnum, DateTime
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel
from app.utils.enums import ActivityType


class UserActivity(BaseModel):
    """User activity tracking model"""
    
    __tablename__ = "user_activities"
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Activity details
    activity_type = Column(SQLAEnum(ActivityType, validate_strings=True, create_constraint=True), nullable=False)
    activity_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Metadata
    extra_data = Column(JSON, nullable=True)  # Additional activity data
    session_id = Column(String(255), nullable=True)  # User session ID
    ip_address = Column(String(45), nullable=True)  # User IP address
    user_agent = Column(String(500), nullable=True)  # User agent string
    
    # Performance metrics
    duration = Column(Float, nullable=True)  # Activity duration in seconds
    success = Column(Boolean, default=True)  # Whether activity was successful
    error_message = Column(Text, nullable=True)  # Error message if failed
    
    # Context
    platform = Column(String(50), nullable=True)  # Platform (telegram, web, etc.)
    feature_used = Column(String(100), nullable=True)  # Specific feature used
    
    # Relationship
    user = relationship("User", back_populates="activities")
    
    def __repr__(self) -> str:
        return f"<UserActivity(id={self.id}, user_id={self.user_id}, type={self.activity_type})>"
    
    @property
    def is_analysis_activity(self) -> bool:
        """Check if activity is analysis-related"""
        return self.activity_type == ActivityType.ANALYSIS_COMPLETED
    
    @property
    def is_successful(self) -> bool:
        """Check if activity was successful"""
        return self.success and not self.error_message
    
    def get_summary(self) -> dict:
        """Get activity summary"""
        return {
            "id": self.id,
            "activity_type": self.activity_type.value,
            "activity_name": self.activity_name,
            "success": self.success,
            "duration": self.duration,
            "created_at": self.created_at.isoformat(),
            "platform": self.platform
        }
    
    @classmethod
    def create_activity(
        cls,
        user_id: int,
        activity_type: ActivityType,
        activity_name: str,
        description: str = None,
        extra_data: dict = None,
        duration: float = None
    ) -> "UserActivity":
        """Create new user activity"""
        return cls(
            user_id=user_id,
            activity_type=activity_type,
            activity_name=activity_name,
            description=description,
            extra_data=extra_data,
            duration=duration
        )


class UserAchievement(BaseModel):
    """User achievements model"""
    
    __tablename__ = "user_achievements"
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Achievement details
    achievement_id = Column(String(100), nullable=False, index=True)
    achievement_name = Column(String(255), nullable=False)
    achievement_description = Column(Text, nullable=True)
    
    # Progress
    current_progress = Column(Integer, default=0)
    target_progress = Column(Integer, nullable=False)
    is_completed = Column(Boolean, default=False)
    completion_date = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    category = Column(String(100), nullable=True)  # Achievement category
    difficulty = Column(String(50), nullable=True)  # easy, medium, hard
    points = Column(Integer, default=0)  # Points awarded
    badge_url = Column(String(500), nullable=True)  # Badge image URL
    
    # Additional data
    unlock_criteria = Column(JSON, nullable=True)  # Criteria for unlocking
    rewards = Column(JSON, nullable=True)  # Rewards for completion
    
    # Status
    is_hidden = Column(Boolean, default=False)  # Hidden until unlocked
    is_special = Column(Boolean, default=False)  # Special/rare achievement
    
    # Relationship
    user = relationship("User", back_populates="achievements")
    
    def __repr__(self) -> str:
        return f"<UserAchievement(id={self.id}, user_id={self.user_id}, name={self.achievement_name})>"
    
    @property
    def progress_percentage(self) -> float:
        """Get progress as percentage"""
        if self.target_progress <= 0:
            return 100.0
        
        return min(100.0, (self.current_progress / self.target_progress) * 100)
    
    @property
    def is_unlocked(self) -> bool:
        """Check if achievement is unlocked (visible to user)"""
        return not self.is_hidden or self.current_progress > 0
    
    @property
    def progress_text(self) -> str:
        """Get progress as text"""
        return f"{self.current_progress}/{self.target_progress}"
    
    @property
    def difficulty_emoji(self) -> str:
        """Get emoji for difficulty"""
        difficulty_emojis = {
            "easy": "🟢",
            "medium": "🟡",
            "hard": "🔴"
        }
        return difficulty_emojis.get(self.difficulty, "⚪")
    
    def update_progress(self, amount: int) -> bool:
        """
        Update achievement progress
        Returns True if achievement was completed
        """
        self.current_progress = min(self.target_progress, self.current_progress + amount)
        
        if not self.is_completed and self.current_progress >= self.target_progress:
            self.complete()
            return True
        
        return False
    
    def complete(self) -> None:
        """Mark achievement as completed"""
        self.is_completed = True
        self.completion_date = func.now()
        self.current_progress = self.target_progress
    
    def reset(self) -> None:
        """Reset achievement progress"""
        self.current_progress = 0
        self.is_completed = False
        self.completion_date = None
    
    def get_summary(self) -> dict:
        """Get achievement summary"""
        return {
            "id": self.id,
            "achievement_id": self.achievement_id,
            "achievement_name": self.achievement_name,
            "current_progress": self.current_progress,
            "target_progress": self.target_progress,
            "progress_percentage": self.progress_percentage,
            "is_completed": self.is_completed,
            "completion_date": self.completion_date.isoformat() if self.completion_date else None,
            "category": self.category,
            "difficulty": self.difficulty,
            "points": self.points,
            "is_unlocked": self.is_unlocked
        }
    
    @classmethod
    def create_achievement(
        cls,
        user_id: int,
        achievement_id: str,
        achievement_name: str,
        target_progress: int,
        category: str = None,
        difficulty: str = "easy",
        points: int = 10
    ) -> "UserAchievement":
        """Create new user achievement"""
        return cls(
            user_id=user_id,
            achievement_id=achievement_id,
            achievement_name=achievement_name,
            target_progress=target_progress,
            category=category,
            difficulty=difficulty,
            points=points
        ) 