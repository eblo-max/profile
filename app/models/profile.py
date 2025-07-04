"""Partner profile model"""

from sqlalchemy import (
    Column, Integer, String, Text, Float, ForeignKey, 
    Boolean, JSON, Enum as SQLAEnum, CheckConstraint
)
from sqlalchemy.orm import relationship, validates

from app.models.base import BaseModel
from app.utils.enums import UrgencyLevel


class PartnerProfile(BaseModel):
    """Partner profile model"""
    
    __tablename__ = "partner_profiles"
    __table_args__ = (
        CheckConstraint('manipulation_risk >= 0 AND manipulation_risk <= 10', name='ck_manipulation_risk_range'),
        CheckConstraint('overall_compatibility >= 0 AND overall_compatibility <= 1', name='ck_overall_compatibility_range'),
    )
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Profile basic info
    partner_name = Column(String(255), nullable=True)
    partner_description = Column(Text, nullable=True)
    
    # Questionnaire answers
    questionnaire_answers = Column(JSON, nullable=False)  # Dict of question_id -> answer
    
    # Profile analysis results
    personality_type = Column(String(100), nullable=True)  # Detected personality type
    manipulation_risk = Column(Float, nullable=False)  # Risk score 1-10
    red_flags = Column(JSON, nullable=True)  # List of detected red flags
    positive_traits = Column(JSON, nullable=True)  # List of positive traits
    warning_signs = Column(JSON, nullable=True)  # List of warning signs
    
    # Detailed analysis
    psychological_profile = Column(Text, nullable=True)  # AI-generated profile
    relationship_advice = Column(Text, nullable=True)  # Relationship recommendations
    communication_tips = Column(Text, nullable=True)  # Communication advice
    
    # Risk assessment
    urgency_level = Column(SQLAEnum(UrgencyLevel, validate_strings=True, create_constraint=True), nullable=False)
    overall_compatibility = Column(Float, nullable=True)  # Compatibility score
    trust_indicators = Column(JSON, nullable=True)  # Trust/distrust indicators
    
    # Metadata
    confidence_score = Column(Float, nullable=True)  # AI confidence in profile
    processing_time = Column(Float, nullable=True)  # Time taken for analysis
    ai_model_used = Column(String(50), nullable=True)  # Which AI model was used
    
    # Status
    is_completed = Column(Boolean, default=False)
    is_shared = Column(Boolean, default=False)
    
    # Relationship
    user = relationship("User", back_populates="partner_profiles")
    
    def __repr__(self) -> str:
        return f"<PartnerProfile(id={self.id}, user_id={self.user_id}, risk={self.manipulation_risk})>"
    
    @property
    def is_high_risk(self) -> bool:
        """Check if profile indicates high risk partner"""
        return self.manipulation_risk >= 7.0 or self.urgency_level in [UrgencyLevel.HIGH, UrgencyLevel.CRITICAL]
    
    @property
    def is_safe(self) -> bool:
        """Check if profile indicates safe partner"""
        return self.manipulation_risk <= 3.0 and self.urgency_level == UrgencyLevel.LOW
    
    @property
    def risk_emoji(self) -> str:
        """Get emoji representing risk level"""
        if self.manipulation_risk >= 8.0:
            return "🔴"
        elif self.manipulation_risk >= 6.0:
            return "🟠"
        elif self.manipulation_risk >= 4.0:
            return "🟡"
        else:
            return "🟢"
    
    @property
    def safety_summary(self) -> str:
        """Get safety summary text"""
        if self.manipulation_risk >= 8.0:
            return "ВЫСОКИЙ РИСК - требуется осторожность"
        elif self.manipulation_risk >= 6.0:
            return "Средний риск - обратите внимание на красные флаги"
        elif self.manipulation_risk >= 4.0:
            return "Низкий риск - в целом безопасно"
        else:
            return "Минимальный риск - хорошие показатели"
    
    def get_summary(self) -> dict:
        """Get profile summary"""
        return {
            "id": self.id,
            "partner_name": self.partner_name,
            "manipulation_risk": self.manipulation_risk,
            "urgency_level": self.urgency_level.value,
            "red_flags_count": len(self.red_flags or []),
            "positive_traits_count": len(self.positive_traits or []),
            "created_at": self.created_at.isoformat(),
            "is_high_risk": self.is_high_risk,
            "safety_summary": self.safety_summary
        }

    @validates("manipulation_risk")
    def validate_manipulation_risk(self, key, value):
        assert 0 <= value <= 10, "manipulation_risk должен быть в диапазоне 0-10"
        return value

    @validates("overall_compatibility")
    def validate_overall_compatibility(self, key, value):
        if value is not None:
            assert 0 <= value <= 1, "overall_compatibility должен быть в диапазоне 0-1"
        return value 