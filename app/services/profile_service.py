"""Partner profile service for psychological profiling"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload

from app.models.profile import PartnerProfile
from app.models.user import User
from app.services.ai_service import AIService
from app.utils.enums import SubscriptionType
from app.core.logging import logger
from app.utils.enums import UrgencyLevel


class ProfileService:
    """Service for partner profile management"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.ai_service = AIService()
    
    async def create_profile(
        self,
        user_id: int,
        name: str,
        description: str,
        questionnaire_data: Dict[str, Any]
    ) -> Optional[PartnerProfile]:
        """Create new partner profile based on questionnaire"""
        try:
            # Check user subscription limits
            user_result = await self.session.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            if not user:
                return None
            
            # Check profile limits based on subscription
            profile_count = await self._get_user_profile_count(user_id)
            max_profiles = self._get_max_profiles(user.subscription_type)
            
            if profile_count >= max_profiles:
                logger.warning(f"User {user_id} exceeded profile limit")
                return None
            
            # Generate psychological analysis
            ai_analysis = await self.ai_service.analyze_partner_profile(
                questionnaire_data=questionnaire_data,
                user_subscription=user.subscription_type.value
            )
            
            if not ai_analysis:
                return None
            
            # Create profile
            profile = PartnerProfile(
                user_id=user_id,
                name=name,
                description=description,
                
                # Questionnaire responses
                questionnaire_responses=questionnaire_data,
                
                # AI Analysis results
                personality_traits=ai_analysis.get('personality_traits', {}),
                communication_style=ai_analysis.get('communication_style', {}),
                emotional_patterns=ai_analysis.get('emotional_patterns', {}),
                attachment_style=ai_analysis.get('attachment_style', ''),
                red_flags=ai_analysis.get('red_flags', []),
                green_flags=ai_analysis.get('green_flags', []),
                
                # Assessments
                compatibility_factors=ai_analysis.get('compatibility_factors', {}),
                relationship_potential=ai_analysis.get('relationship_potential', 0.0),
                risk_assessment=ai_analysis.get('risk_assessment', 'low'),
                
                # Insights
                strengths=ai_analysis.get('strengths', []),
                concerns=ai_analysis.get('concerns', []),
                recommendations=ai_analysis.get('recommendations', []),
                summary=ai_analysis.get('summary', '')
            )
            
            self.session.add(profile)
            await self.session.commit()
            await self.session.refresh(profile)
            
            logger.info(f"Partner profile created for user {user_id}: {name}")
            return profile
            
        except Exception as e:
            logger.error(f"Error creating profile: {e}")
            await self.session.rollback()
            return None

    async def create_profile_from_profiler(
        self,
        user_id: int,
        partner_name: str,
        partner_description: str,
        partner_basic_info: str,
        questions: List[Dict[str, Any]],
        answers: Dict[str, int],
        analysis_result: Dict[str, Any]
    ) -> Optional[PartnerProfile]:
        """Create partner profile from profiler data"""
        try:
            # Check user subscription limits
            user_result = await self.session.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            if not user:
                return None
            
            # Check profile limits based on subscription
            profile_count = await self._get_user_profile_count(user_id)
            max_profiles = self._get_max_profiles(user.subscription_type)
            
            if profile_count >= max_profiles:
                logger.warning(f"User {user_id} exceeded profile limit")
                return None
            
            # Combine description and basic info
            full_description = f"{partner_description}\n\nБазовая информация: {partner_basic_info}"
            
            # Extract data from analysis result
            overall_risk = analysis_result.get('overall_risk_score', analysis_result.get('manipulation_risk', 0))
            
            # Ensure manipulation_risk is in 0-10 scale
            if isinstance(overall_risk, float) and overall_risk <= 10:
                manipulation_risk = float(overall_risk)  # Already in 0-10 scale
            else:
                manipulation_risk = float(overall_risk) / 10.0  # Convert 0-100 to 0-10 scale
            
            # Ensure it's within bounds
            manipulation_risk = max(0.0, min(10.0, manipulation_risk))
            
            # Extract urgency level
            urgency_map = {
                'LOW': UrgencyLevel.LOW,
                'MEDIUM': UrgencyLevel.MEDIUM,
                'HIGH': UrgencyLevel.HIGH,
                'CRITICAL': UrgencyLevel.CRITICAL
            }
            urgency_level = urgency_map.get(
                analysis_result.get('urgency_level', 'LOW').upper(),
                UrgencyLevel.LOW
            )
            
            # Create profile
            profile = PartnerProfile(
                user_id=user_id,
                partner_name=partner_name,
                partner_description=full_description,
                
                # Questionnaire data
                questionnaire_answers=answers,
                
                # Analysis results
                personality_type=analysis_result.get('personality_type', ''),
                manipulation_risk=manipulation_risk,
                red_flags=analysis_result.get('red_flags', []),
                positive_traits=analysis_result.get('positive_traits', []),
                warning_signs=analysis_result.get('warning_signs', analysis_result.get('safety_alerts', [])),
                
                # Detailed analysis
                psychological_profile=analysis_result.get('psychological_profile', ''),
                relationship_advice=analysis_result.get('relationship_advice', ''),
                communication_tips=analysis_result.get('communication_tips', ''),
                
                # Risk assessment
                urgency_level=urgency_level,
                overall_compatibility=analysis_result.get('compatibility_score', 0.0),
                trust_indicators=analysis_result.get('trust_indicators', {}),
                
                # Metadata
                confidence_score=analysis_result.get('confidence_score', 0.0),
                ai_model_used=analysis_result.get('ai_model_used', 'claude-3-sonnet'),
                
                # Status
                is_completed=True,
                is_shared=False
            )
            
            self.session.add(profile)
            await self.session.commit()
            await self.session.refresh(profile)
            
            logger.info(f"Partner profile created from profiler for user {user_id}: {partner_name}")
            return profile
            
        except Exception as e:
            logger.error(f"Error creating profile from profiler: {e}")
            await self.session.rollback()
            return None
    
    async def get_user_profiles(
        self,
        user_id: int,
        limit: int = 10,
        offset: int = 0
    ) -> List[PartnerProfile]:
        """Get user's partner profiles"""
        try:
            result = await self.session.execute(
                select(PartnerProfile)
                .where(PartnerProfile.user_id == user_id)
                .order_by(desc(PartnerProfile.created_at))
                .limit(limit)
                .offset(offset)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting user profiles: {e}")
            return []
    
    async def get_profile_by_id(
        self,
        profile_id: int,
        user_id: int
    ) -> Optional[PartnerProfile]:
        """Get specific profile by ID (with user verification)"""
        try:
            result = await self.session.execute(
                select(PartnerProfile)
                .where(
                    PartnerProfile.id == profile_id,
                    PartnerProfile.user_id == user_id
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting profile by ID: {e}")
            return None
    
    async def update_profile(
        self,
        profile_id: int,
        user_id: int,
        updates: Dict[str, Any]
    ) -> Optional[PartnerProfile]:
        """Update existing profile"""
        try:
            profile = await self.get_profile_by_id(profile_id, user_id)
            if not profile:
                return None
            
            # Update basic fields
            if 'name' in updates:
                profile.name = updates['name']
            if 'description' in updates:
                profile.description = updates['description']
            
            # If questionnaire data is updated, regenerate analysis
            if 'questionnaire_responses' in updates:
                profile.questionnaire_responses = updates['questionnaire_responses']
                
                # Get user for subscription check
                user_result = await self.session.execute(
                    select(User).where(User.id == user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if user:
                    # Regenerate AI analysis
                    ai_analysis = await self.ai_service.analyze_partner_profile(
                        questionnaire_data=updates['questionnaire_responses'],
                        user_subscription=user.subscription_type.value
                    )
                    
                    if ai_analysis:
                        profile.personality_traits = ai_analysis.get('personality_traits', {})
                        profile.communication_style = ai_analysis.get('communication_style', {})
                        profile.emotional_patterns = ai_analysis.get('emotional_patterns', {})
                        profile.attachment_style = ai_analysis.get('attachment_style', '')
                        profile.red_flags = ai_analysis.get('red_flags', [])
                        profile.green_flags = ai_analysis.get('green_flags', [])
                        profile.compatibility_factors = ai_analysis.get('compatibility_factors', {})
                        profile.relationship_potential = ai_analysis.get('relationship_potential', 0.0)
                        profile.risk_assessment = ai_analysis.get('risk_assessment', 'low')
                        profile.strengths = ai_analysis.get('strengths', [])
                        profile.concerns = ai_analysis.get('concerns', [])
                        profile.recommendations = ai_analysis.get('recommendations', [])
                        profile.summary = ai_analysis.get('summary', '')
            
            profile.updated_at = datetime.utcnow()
            
            await self.session.commit()
            await self.session.refresh(profile)
            
            logger.info(f"Profile {profile_id} updated for user {user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Error updating profile: {e}")
            await self.session.rollback()
            return None
    
    async def delete_profile(
        self,
        profile_id: int,
        user_id: int
    ) -> bool:
        """Delete profile (with user verification)"""
        try:
            profile = await self.get_profile_by_id(profile_id, user_id)
            if not profile:
                return False
            
            await self.session.delete(profile)
            await self.session.commit()
            
            logger.info(f"Profile {profile_id} deleted for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting profile: {e}")
            await self.session.rollback()
            return False
    
    async def get_profile_recommendations(
        self,
        profile_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Get detailed recommendations for a profile"""
        try:
            profile = await self.get_profile_by_id(profile_id, user_id)
            if not profile:
                return {}
            
            # Generate additional AI recommendations
            additional_insights = await self.ai_service.generate_profile_insights(
                profile_data={
                    'personality_traits': profile.personality_traits,
                    'communication_style': profile.communication_style,
                    'emotional_patterns': profile.emotional_patterns,
                    'red_flags': profile.red_flags,
                    'green_flags': profile.green_flags
                }
            )
            
            return {
                'basic_recommendations': profile.recommendations,
                'strengths': profile.strengths,
                'concerns': profile.concerns,
                'additional_insights': additional_insights.get('insights', []),
                'communication_tips': additional_insights.get('communication_tips', []),
                'warning_signs': additional_insights.get('warning_signs', []),
                'growth_opportunities': additional_insights.get('growth_opportunities', [])
            }
            
        except Exception as e:
            logger.error(f"Error getting profile recommendations: {e}")
            return {}
    
    async def _get_user_profile_count(self, user_id: int) -> int:
        """Get count of user's profiles"""
        try:
            result = await self.session.execute(
                select(func.count(PartnerProfile.id))
                .where(PartnerProfile.user_id == user_id)
            )
            return result.scalar() or 0
        except Exception as e:
            logger.error(f"Error getting profile count: {e}")
            return 0
    
    def _get_max_profiles(self, subscription_type: SubscriptionType) -> int:
        """Get maximum profiles allowed for subscription type"""
        if subscription_type == SubscriptionType.FREE:
            return 51
        elif subscription_type == SubscriptionType.PREMIUM:
            return 55
        elif subscription_type == SubscriptionType.VIP:
            return 70
        return 51
    
    async def generate_compatibility_report(
        self,
        profile1_id: int,
        profile2_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Generate compatibility report between two profiles"""
        try:
            # Get both profiles
            profile1 = await self.get_profile_by_id(profile1_id, user_id)
            profile2 = await self.get_profile_by_id(profile2_id, user_id)
            
            if not profile1 or not profile2:
                return {}
            
            # Generate AI compatibility analysis
            compatibility_analysis = await self.ai_service.analyze_compatibility(
                profile1_data={
                    'personality_traits': profile1.personality_traits,
                    'communication_style': profile1.communication_style,
                    'emotional_patterns': profile1.emotional_patterns,
                    'attachment_style': profile1.attachment_style
                },
                profile2_data={
                    'personality_traits': profile2.personality_traits,
                    'communication_style': profile2.communication_style,
                    'emotional_patterns': profile2.emotional_patterns,
                    'attachment_style': profile2.attachment_style
                }
            )
            
            return {
                'profile1_name': profile1.name,
                'profile2_name': profile2.name,
                'compatibility_score': compatibility_analysis.get('compatibility_score', 0.0),
                'strengths': compatibility_analysis.get('strengths', []),
                'challenges': compatibility_analysis.get('challenges', []),
                'recommendations': compatibility_analysis.get('recommendations', []),
                'communication_compatibility': compatibility_analysis.get('communication_compatibility', {}),
                'emotional_compatibility': compatibility_analysis.get('emotional_compatibility', {}),
                'long_term_potential': compatibility_analysis.get('long_term_potential', 0.0),
                'areas_for_growth': compatibility_analysis.get('areas_for_growth', [])
            }
            
        except Exception as e:
            logger.error(f"Error generating compatibility report: {e}")
            return {} 