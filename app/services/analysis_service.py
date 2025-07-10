"""Text analysis service for relationship content analysis"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.models.analysis import TextAnalysis
from app.models.user import User
from app.services.ai_service import AIService
from app.utils.enums import AnalysisType, RiskLevel, SubscriptionType
from app.core.logging import logger


class AnalysisService:
    """Service for text analysis operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.ai_service = AIService()
    
    async def analyze_text(
        self,
        user_id: int,
        text: str,
        analysis_type: AnalysisType = AnalysisType.TEXT_ANALYSIS,
        context: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[TextAnalysis]:
        """Analyze text for relationship insights"""
        try:
            # Get user to check subscription
            user_result = await self.session.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            if not user:
                return None
            
            # Analyze with AI
            analysis_result = await self.ai_service.analyze_text(
                text=text,
                analysis_type=analysis_type.value,
                context=context,
                user_subscription=user.subscription_type.value
            )
            
            if not analysis_result:
                return None
            
            # Create analysis record
            analysis = TextAnalysis(
                user_id=user_id,
                text_content=text,
                analysis_type=analysis_type,
                context=context or "",
                
                # AI Analysis results
                manipulation_score=analysis_result.get('manipulation_score', 0),
                emotional_state=analysis_result.get('emotional_state', {}),
                communication_style=analysis_result.get('communication_style', {}),
                red_flags=analysis_result.get('red_flags', []),
                risk_assessment=RiskLevel(analysis_result.get('risk_level', 'low')),
                
                # Insights and recommendations
                key_insights=analysis_result.get('key_insights', []),
                recommendations=analysis_result.get('recommendations', []),
                summary=analysis_result.get('summary', ''),
                confidence_score=analysis_result.get('confidence_score', 0.0),
                
                metadata=metadata or {}
            )
            
            self.session.add(analysis)
            await self.session.commit()
            await self.session.refresh(analysis)
            
            logger.info(f"Text analysis completed for user {user_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in text analysis: {e}")
            await self.session.rollback()
            return None
    
    async def get_user_analyses(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> List[TextAnalysis]:
        """Get user's analysis history"""
        try:
            result = await self.session.execute(
                select(TextAnalysis)
                .where(TextAnalysis.user_id == user_id)
                .order_by(desc(TextAnalysis.created_at))
                .limit(limit)
                .offset(offset)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting user analyses: {e}")
            return []
    
    async def get_analysis_by_id(
        self,
        analysis_id: int,
        user_id: int
    ) -> Optional[TextAnalysis]:
        """Get specific analysis by ID (with user verification)"""
        try:
            result = await self.session.execute(
                select(TextAnalysis)
                .where(
                    TextAnalysis.id == analysis_id,
                    TextAnalysis.user_id == user_id
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting analysis by ID: {e}")
            return None
    
    async def get_analysis_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user's analysis statistics"""
        try:
            # Total analyses
            total_result = await self.session.execute(
                select(TextAnalysis)
                .where(TextAnalysis.user_id == user_id)
            )
            analyses = total_result.scalars().all()
            
            if not analyses:
                return {
                    'total_analyses': 0,
                    'average_risk': 0.0,
                    'risk_distribution': {},
                    'recent_trend': 'no_data'
                }
            
            # Calculate statistics
            total_count = len(analyses)
            risk_counts = {}
            risk_scores = []
            
            for analysis in analyses:
                risk_level = analysis.risk_assessment.value
                risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
                
                # Convert risk level to numeric score for averaging
                risk_score_map = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
                risk_scores.append(risk_score_map.get(risk_level, 1))
            
            average_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
            
            # Risk distribution as percentages
            risk_distribution = {
                level: (count / total_count) * 100 
                for level, count in risk_counts.items()
            }
            
            # Recent trend (last 5 vs previous 5)
            recent_trend = 'stable'
            if total_count >= 10:
                recent_5 = risk_scores[:5]
                previous_5 = risk_scores[5:10]
                
                recent_avg = sum(recent_5) / 5
                previous_avg = sum(previous_5) / 5
                
                if recent_avg > previous_avg + 0.5:
                    recent_trend = 'increasing'
                elif recent_avg < previous_avg - 0.5:
                    recent_trend = 'decreasing'
            
            return {
                'total_analyses': total_count,
                'average_risk': round(average_risk, 2),
                'risk_distribution': risk_distribution,
                'recent_trend': recent_trend
            }
            
        except Exception as e:
            logger.error(f"Error getting analysis stats: {e}")
            return {}
    
    async def delete_analysis(
        self,
        analysis_id: int,
        user_id: int
    ) -> bool:
        """Delete analysis (with user verification)"""
        try:
            analysis = await self.get_analysis_by_id(analysis_id, user_id)
            if not analysis:
                return False
            
            await self.session.delete(analysis)
            await self.session.commit()
            
            logger.info(f"Analysis {analysis_id} deleted for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting analysis: {e}")
            await self.session.rollback()
            return False
    
    async def bulk_analyze(
        self,
        user_id: int,
        texts: List[str],
        analysis_type: AnalysisType = AnalysisType.TEXT_ANALYSIS
    ) -> List[TextAnalysis]:
        """Analyze multiple texts in bulk (premium feature)"""
        try:
            # Check user subscription
            user_result = await self.session.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user or user.subscription_type == SubscriptionType.FREE:
                logger.warning(f"Bulk analysis attempted by non-premium user {user_id}")
                return []
            
            analyses = []
            
            for i, text in enumerate(texts):
                try:
                    analysis = await self.analyze_text(
                        user_id=user_id,
                        text=text,
                        analysis_type=analysis_type,
                        context=f"Bulk analysis item {i+1}/{len(texts)}",
                        metadata={'bulk_analysis': True, 'position': i+1, 'total': len(texts)}
                    )
                    
                    if analysis:
                        analyses.append(analysis)
                        
                except Exception as e:
                    logger.error(f"Error in bulk analysis item {i+1}: {e}")
                    continue
            
            logger.info(f"Bulk analysis completed: {len(analyses)}/{len(texts)} successful")
            return analyses
            
        except Exception as e:
            logger.error(f"Error in bulk analysis: {e}")
            return []
    
    async def get_insights_summary(self, user_id: int) -> Dict[str, Any]:
        """Get summarized insights from user's analyses"""
        try:
            # Get recent analyses (last 30 days)
            from datetime import timedelta
            since = datetime.utcnow() - timedelta(days=30)
            
            result = await self.session.execute(
                select(TextAnalysis)
                .where(
                    TextAnalysis.user_id == user_id,
                    TextAnalysis.created_at >= since
                )
                .order_by(desc(TextAnalysis.created_at))
            )
            
            analyses = result.scalars().all()
            
            if not analyses:
                return {'message': 'Недостаточно данных для анализа'}
            
            # Aggregate insights
            all_red_flags = []
            all_insights = []
            risk_levels = []
            manipulation_scores = []
            
            for analysis in analyses:
                all_red_flags.extend(analysis.red_flags or [])
                all_insights.extend(analysis.key_insights or [])
                risk_levels.append(analysis.risk_assessment.value)
                manipulation_scores.append(analysis.manipulation_score or 0)
            
            # Find most common patterns
            from collections import Counter
            
            common_red_flags = Counter(all_red_flags).most_common(5)
            common_insights = Counter(all_insights).most_common(5)
            
            # Calculate averages
            avg_manipulation = sum(manipulation_scores) / len(manipulation_scores) if manipulation_scores else 0
            most_common_risk = Counter(risk_levels).most_common(1)[0][0] if risk_levels else 'low'
            
            return {
                'period': '30 дней',
                'total_analyses': len(analyses),
                'average_manipulation_score': round(avg_manipulation, 2),
                'most_common_risk_level': most_common_risk,
                'common_red_flags': [flag for flag, count in common_red_flags],
                'key_patterns': [insight for insight, count in common_insights],
                'trend_summary': self._generate_trend_summary(analyses)
            }
            
        except Exception as e:
            logger.error(f"Error getting insights summary: {e}")
            return {}
    
    def _generate_trend_summary(self, analyses: List[TextAnalysis]) -> str:
        """Generate a summary of trends in analyses"""
        if len(analyses) < 3:
            return "Недостаточно данных для определения тенденций"
        
        # Check risk trend
        risk_score_map = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        scores = [risk_score_map.get(a.risk_assessment.value, 1) for a in analyses]
        
        # Compare first half vs second half
        mid = len(scores) // 2
        first_half_avg = sum(scores[:mid]) / mid if mid > 0 else 0
        second_half_avg = sum(scores[mid:]) / (len(scores) - mid) if len(scores) - mid > 0 else 0
        
        if second_half_avg > first_half_avg + 0.5:
            return "Уровень риска в отношениях растет. Рекомендуется более внимательно анализировать общение."
        elif second_half_avg < first_half_avg - 0.5:
            return "Уровень риска в отношениях снижается. Это позитивная тенденция!"
        else:
            return "Уровень риска в отношениях остается стабильным." 