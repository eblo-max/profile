"""Compatibility test model"""

from sqlalchemy import (
    Column, Integer, String, Text, Float, ForeignKey, 
    Boolean, JSON
)
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class CompatibilityTest(BaseModel):
    """Compatibility test model"""
    
    __tablename__ = "compatibility_tests"
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Test participants
    user_name = Column(String(255), nullable=True)
    partner_name = Column(String(255), nullable=True)
    
    # Questionnaire answers
    user_answers = Column(JSON, nullable=False)  # Dict of question_id -> answer
    partner_answers = Column(JSON, nullable=False)  # Dict of question_id -> answer
    
    # Compatibility results
    overall_compatibility = Column(Float, nullable=False)  # Overall score 1-10
    communication_compatibility = Column(Float, nullable=True)  # Communication score
    values_compatibility = Column(Float, nullable=True)  # Values alignment score
    lifestyle_compatibility = Column(Float, nullable=True)  # Lifestyle compatibility
    emotional_compatibility = Column(Float, nullable=True)  # Emotional compatibility
    
    # Detailed analysis
    strengths = Column(JSON, nullable=True)  # List of relationship strengths
    challenges = Column(JSON, nullable=True)  # List of potential challenges
    recommendations = Column(JSON, nullable=True)  # List of recommendations
    
    # Analysis text
    compatibility_analysis = Column(Text, nullable=True)  # AI-generated analysis
    relationship_advice = Column(Text, nullable=True)  # Relationship advice
    growth_areas = Column(Text, nullable=True)  # Areas for improvement
    
    # Comparison data
    similarity_score = Column(Float, nullable=True)  # How similar partners are
    complement_score = Column(Float, nullable=True)  # How well they complement each other
    conflict_potential = Column(Float, nullable=True)  # Potential for conflicts
    
    # Specific compatibility areas
    communication_style_match = Column(Float, nullable=True)
    conflict_resolution_match = Column(Float, nullable=True)
    life_goals_alignment = Column(Float, nullable=True)
    emotional_needs_match = Column(Float, nullable=True)
    
    # Metadata
    confidence_score = Column(Float, nullable=True)  # AI confidence in results
    processing_time = Column(Float, nullable=True)  # Time taken for analysis
    ai_model_used = Column(String(50), nullable=True)  # Which AI model was used
    
    # Status
    is_completed = Column(Boolean, default=False)
    is_shared = Column(Boolean, default=False)
    
    # Relationship
    user = relationship("User", back_populates="compatibility_tests")
    
    def __repr__(self) -> str:
        return f"<CompatibilityTest(id={self.id}, user_id={self.user_id}, score={self.overall_compatibility})>"
    
    @property
    def compatibility_level(self) -> str:
        """Get compatibility level description"""
        if self.overall_compatibility >= 8.5:
            return "Отличная совместимость"
        elif self.overall_compatibility >= 7.0:
            return "Хорошая совместимость"
        elif self.overall_compatibility >= 5.5:
            return "Средняя совместимость"
        elif self.overall_compatibility >= 4.0:
            return "Низкая совместимость"
        else:
            return "Очень низкая совместимость"
    
    @property
    def compatibility_emoji(self) -> str:
        """Get emoji representing compatibility level"""
        if self.overall_compatibility >= 8.0:
            return "💚"
        elif self.overall_compatibility >= 6.5:
            return "💛"
        elif self.overall_compatibility >= 5.0:
            return "🧡"
        else:
            return "❤️‍🩹"
    
    @property
    def is_highly_compatible(self) -> bool:
        """Check if partners are highly compatible"""
        return self.overall_compatibility >= 7.5
    
    @property
    def needs_attention(self) -> bool:
        """Check if relationship needs attention"""
        return self.overall_compatibility < 5.0 or (self.conflict_potential or 0) > 7.0
    
    def get_summary(self) -> dict:
        """Get compatibility test summary"""
        return {
            "id": self.id,
            "user_name": self.user_name,
            "partner_name": self.partner_name,
            "overall_compatibility": self.overall_compatibility,
            "compatibility_level": self.compatibility_level,
            "strengths_count": len(self.strengths or []),
            "challenges_count": len(self.challenges or []),
            "created_at": self.created_at.isoformat(),
            "is_highly_compatible": self.is_highly_compatible,
            "needs_attention": self.needs_attention
        }
    
    def get_detailed_scores(self) -> dict:
        """Get detailed compatibility scores"""
        return {
            "overall": self.overall_compatibility,
            "communication": self.communication_compatibility,
            "values": self.values_compatibility,
            "lifestyle": self.lifestyle_compatibility,
            "emotional": self.emotional_compatibility,
            "similarity": self.similarity_score,
            "complement": self.complement_score,
            "conflict_potential": self.conflict_potential
        } 