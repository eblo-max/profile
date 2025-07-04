"""Text analysis model"""

from sqlalchemy import (
    Column, Integer, String, Text, Float, ForeignKey, 
    Boolean, JSON, Enum as SQLAEnum
)
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.utils.constants import AnalysisType, UrgencyLevel


class TextAnalysis(BaseModel):
    """Text analysis model"""
    
    __tablename__ = "text_analyses"
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Analysis data
    analysis_type = Column(SQLAEnum(AnalysisType), default=AnalysisType.TEXT_ANALYSIS)
    original_text = Column(Text, nullable=False)
    text_hash = Column(String(64), nullable=False, index=True)  # For deduplication
    
    # Analysis results
    toxicity_score = Column(Float, nullable=False)
    urgency_level = Column(SQLAEnum(UrgencyLevel), nullable=False)
    red_flags = Column(JSON, nullable=True)  # List of detected red flags
    patterns_detected = Column(JSON, nullable=True)  # List of manipulation patterns
    analysis_text = Column(Text, nullable=True)  # AI analysis description
    recommendation = Column(Text, nullable=True)  # AI recommendations
    
    # Metadata
    confidence_score = Column(Float, nullable=True)  # AI confidence in analysis
    processing_time = Column(Float, nullable=True)  # Time taken for analysis
    ai_model_used = Column(String(50), nullable=True)  # Which AI model was used
    
    # Additional analysis data
    keywords = Column(JSON, nullable=True)  # Extracted keywords
    sentiment_score = Column(Float, nullable=True)  # Sentiment analysis score
    reading_time = Column(Integer, nullable=True)  # Estimated reading time in minutes
    
    # Status
    is_processed = Column(Boolean, default=False)
    is_shared = Column(Boolean, default=False)  # User shared this analysis
    
    # Relationship
    user = relationship("User", back_populates="analyses")
    
    def __repr__(self) -> str:
        return f"<TextAnalysis(id={self.id}, user_id={self.user_id}, toxicity={self.toxicity_score})>"
    
    @property
    def is_high_risk(self) -> bool:
        """Check if analysis indicates high risk"""
        return self.urgency_level in [UrgencyLevel.HIGH, UrgencyLevel.CRITICAL]
    
    @property
    def is_critical(self) -> bool:
        """Check if analysis indicates critical risk"""
        return self.urgency_level == UrgencyLevel.CRITICAL
    
    @property
    def risk_emoji(self) -> str:
        """Get emoji representing risk level"""
        risk_emojis = {
            UrgencyLevel.LOW: "🟢",
            UrgencyLevel.MEDIUM: "🟡",
            UrgencyLevel.HIGH: "🟠",
            UrgencyLevel.CRITICAL: "🔴"
        }
        return risk_emojis.get(self.urgency_level, "⚪")
    
    def get_summary(self) -> dict:
        """Get analysis summary"""
        return {
            "id": self.id,
            "toxicity_score": self.toxicity_score,
            "urgency_level": self.urgency_level.value,
            "red_flags_count": len(self.red_flags or []),
            "patterns_count": len(self.patterns_detected or []),
            "created_at": self.created_at.isoformat(),
            "is_high_risk": self.is_high_risk
        } 