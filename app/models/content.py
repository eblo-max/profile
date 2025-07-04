"""Daily content model"""

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, 
    Enum as SQLAEnum, DateTime
)
from sqlalchemy.sql import func

from app.models.base import BaseModel
from app.utils.enums import ContentType


class DailyContent(BaseModel):
    """Daily content model"""
    
    __tablename__ = "daily_content"
    
    # Content details
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(SQLAEnum(ContentType), nullable=False)
    
    # Metadata
    author = Column(String(255), nullable=True)
    source = Column(String(255), nullable=True)
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    
    # Scheduling
    scheduled_date = Column(DateTime(timezone=True), nullable=True)
    published_date = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_published = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)  # Premium content
    
    # Engagement
    views_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    
    # Additional data
    image_url = Column(String(500), nullable=True)
    external_url = Column(String(500), nullable=True)
    reading_time = Column(Integer, nullable=True)  # Minutes
    
    def __repr__(self) -> str:
        return f"<DailyContent(id={self.id}, title={self.title[:50]}, type={self.content_type})>"
    
    @property
    def is_tip(self) -> bool:
        """Check if content is a tip"""
        return self.content_type == ContentType.TIP
    
    @property
    def is_case_study(self) -> bool:
        """Check if content is a case study"""
        return self.content_type == ContentType.CASE_STUDY
    
    @property
    def is_exercise(self) -> bool:
        """Check if content is an exercise"""
        return self.content_type == ContentType.EXERCISE
    
    @property
    def is_quote(self) -> bool:
        """Check if content is a quote"""
        return self.content_type == ContentType.QUOTE
    
    @property
    def engagement_score(self) -> float:
        """Calculate engagement score"""
        if self.views_count == 0:
            return 0.0
        
        # Weighted engagement score
        engagement = (
            (self.likes_count * 2) + 
            (self.shares_count * 3)
        ) / self.views_count
        
        return round(engagement * 100, 2)
    
    @property
    def type_emoji(self) -> str:
        """Get emoji for content type"""
        type_emojis = {
            ContentType.TIP: "💡",
            ContentType.CASE_STUDY: "📚", 
            ContentType.EXERCISE: "🏋️",
            ContentType.QUOTE: "💭"
        }
        return type_emojis.get(self.content_type, "📄")
    
    def increment_views(self) -> None:
        """Increment view count"""
        self.views_count += 1
    
    def increment_likes(self) -> None:
        """Increment likes count"""
        self.likes_count += 1
    
    def increment_shares(self) -> None:
        """Increment shares count"""
        self.shares_count += 1
    
    def publish(self) -> None:
        """Publish the content"""
        self.is_published = True
        self.published_date = func.now()
    
    def unpublish(self) -> None:
        """Unpublish the content"""
        self.is_published = False
        self.published_date = None
    
    def get_summary(self) -> dict:
        """Get content summary"""
        return {
            "id": self.id,
            "title": self.title,
            "content_type": self.content_type.value,
            "is_published": self.is_published,
            "is_premium": self.is_premium,
            "views_count": self.views_count,
            "likes_count": self.likes_count,
            "engagement_score": self.engagement_score,
            "created_at": self.created_at.isoformat(),
            "published_date": self.published_date.isoformat() if self.published_date else None
        } 