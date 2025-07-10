"""AI service for text analysis using Claude with OpenAI fallback"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List

import httpx
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from loguru import logger

from app.core.config import settings
from app.core.redis import redis_client
from app.utils.exceptions import AIServiceError
from app.utils.helpers import safe_json_loads, create_cache_key
from app.prompts.analysis_prompts import (
    TEXT_ANALYSIS_SYSTEM_PROMPT,
    PROFILER_SYSTEM_PROMPT, 
    COMPATIBILITY_SYSTEM_PROMPT,
    get_text_analysis_prompt,
    get_profiler_prompt,
    get_compatibility_prompt
)


class AIService:
    """AI service for psychological analysis"""
    
    def __init__(self):
        # Initialize AI clients
        self.claude_client = AsyncAnthropic(api_key=settings.CLAUDE_API_KEY) if settings.CLAUDE_API_KEY else None
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        
        # Configuration
        self.max_retries = settings.AI_RETRY_ATTEMPTS
        self.retry_delay = settings.AI_RETRY_DELAY
        self.timeout = settings.AI_REQUEST_TIMEOUT
        
        # Rate limiting
        self._request_semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_AI_REQUESTS)
        self._last_requests = {}
    
    async def analyze_text(
        self,
        text: str,
        user_id: int,
        context: str = "",
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze text for manipulation patterns and risks
        
        Args:
            text: Text to analyze
            user_id: User ID for rate limiting
            context: Additional context
            use_cache: Whether to use cache
            
        Returns:
            Analysis results
        """
        start_time = time.time()
        
        # Create cache key
        cache_key = create_cache_key("text_analysis", user_id, hash(text + context))
        
        # Try to get from cache
        if use_cache:
            cached_result = await redis_client.get(cache_key)
            if cached_result:
                logger.info(f"Text analysis cache hit for user {user_id}")
                return cached_result
        
        # Check rate limiting
        await self._check_rate_limit(user_id)
        
        try:
            # Prepare prompt
            user_prompt = get_text_analysis_prompt(text, context)
            
            # Get analysis from AI
            async with self._request_semaphore:
                result = await self._get_ai_response(
                    system_prompt=TEXT_ANALYSIS_SYSTEM_PROMPT,
                    user_prompt=user_prompt,
                    response_format="json"
                )
            
            # Parse and validate response
            analysis = self._parse_analysis_response(result)
            
            # Add metadata
            analysis["processing_time"] = time.time() - start_time
            analysis["ai_model_used"] = self._get_last_model_used()
            
            # Cache result
            if use_cache:
                await redis_client.set(
                    cache_key,
                    analysis,
                    expire=1800  # 30 minutes
                )
            
            logger.info(f"Text analysis completed for user {user_id} in {analysis['processing_time']:.2f}s")
            return analysis
            
        except Exception as e:
            logger.error(f"Text analysis failed for user {user_id}: {e}")
            raise AIServiceError(f"Failed to analyze text: {str(e)}")
    
    async def profile_partner(
        self,
        answers: Dict[str, int],
        user_id: int,
        partner_name: str = "партнер",
        partner_description: str = "",
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Create partner psychological profile using FULL questionnaire (28 questions, 6 blocks)
        
        Args:
            answers: Full questionnaire answers (question_id -> answer_index) 
            user_id: User ID
            partner_name: Partner's name
            partner_description: Partner description
            use_cache: Whether to use cache
            
        Returns:
            Comprehensive profile analysis with safety assessment
        """
        start_time = time.time()
        
        # Create cache key
        answers_hash = hash(json.dumps(answers, sort_keys=True) + partner_name + partner_description)
        cache_key = create_cache_key("partner_profile_full", user_id, answers_hash)
        
        # Try cache
        if use_cache:
            cached_result = await redis_client.get(cache_key)
            if cached_result:
                logger.info(f"Partner profile cache hit for user {user_id}")
                return cached_result
        
        # Check rate limiting
        await self._check_rate_limit(user_id)
        
        try:
            # Import full profiler functions
            from app.prompts.profiler_full_questions import calculate_weighted_scores, get_safety_alerts
            from app.prompts.profiler_full_prompts import get_profiler_full_analysis_prompt
            
            # Calculate scores and safety alerts
            scores = calculate_weighted_scores(answers)
            safety_alerts = get_safety_alerts(answers)
            
            # Prepare prompt for AI analysis
            user_prompt = get_profiler_full_analysis_prompt(
                partner_name=partner_name,
                partner_description=partner_description,
                answers=answers,
                block_scores=scores["block_scores"],
                overall_risk_score=scores["overall_risk_score"]
            )
            
            # Get analysis from AI
            async with self._request_semaphore:
                result = await self._get_ai_response(
                    system_prompt=PROFILER_SYSTEM_PROMPT,
                    user_prompt=user_prompt,
                    response_format="text",  # Full version uses text format for rich content
                    max_tokens=8000  # Increased for comprehensive analysis
                )
            
            # Create comprehensive profile
            profile = {
                "analysis": result,
                "block_scores": scores["block_scores"],
                "overall_risk_score": scores["overall_risk_score"],
                "urgency_level": scores["urgency_level"].value,
                "safety_alerts": safety_alerts,
                "partner_name": partner_name,
                "partner_description": partner_description,
                "processing_time": time.time() - start_time,
                "ai_model_used": self._get_last_model_used(),
                "total_questions": 28,
                "questionnaire_version": "full_v1.0"
            }
            
            # Cache result
            if use_cache:
                await redis_client.set(
                    cache_key,
                    profile,
                    expire=3600  # 1 hour
                )
            
            logger.info(f"Full partner profile completed for user {user_id} in {profile['processing_time']:.2f}s, risk: {profile['urgency_level']}")
            return profile
            
        except Exception as e:
            logger.error(f"Partner profiling failed for user {user_id}: {e}")
            # Return fallback analysis with calculated scores
            try:
                from app.prompts.profiler_full_questions import calculate_weighted_scores
                scores = calculate_weighted_scores(answers)
                return self._create_full_fallback_analysis(answers, scores, partner_name)
            except:
                return self._create_basic_fallback_analysis(answers, partner_name)
    
    async def analyze_compatibility(
        self,
        user_answers: Dict[int, str],
        partner_answers: Dict[int, str],
        user_id: int,
        user_name: str = "Пользователь",
        partner_name: str = "Партнер",
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze compatibility between two people
        
        Args:
            user_answers: User's answers
            partner_answers: Partner's answers
            user_id: User ID
            user_name: User's name
            partner_name: Partner's name
            use_cache: Whether to use cache
            
        Returns:
            Compatibility analysis
        """
        start_time = time.time()
        
        # Create cache key
        combined_hash = hash(
            json.dumps(user_answers, sort_keys=True) + 
            json.dumps(partner_answers, sort_keys=True)
        )
        cache_key = create_cache_key("compatibility", user_id, combined_hash)
        
        # Try cache
        if use_cache:
            cached_result = await redis_client.get(cache_key)
            if cached_result:
                logger.info(f"Compatibility analysis cache hit for user {user_id}")
                return cached_result
        
        # Check rate limiting
        await self._check_rate_limit(user_id)
        
        try:
            # Prepare prompt
            user_prompt = get_compatibility_prompt(
                user_answers, partner_answers, user_name, partner_name
            )
            
            # Get analysis from AI
            async with self._request_semaphore:
                result = await self._get_ai_response(
                    system_prompt=COMPATIBILITY_SYSTEM_PROMPT,
                    user_prompt=user_prompt,
                    response_format="json"
                )
            
            # Parse response
            compatibility = self._parse_compatibility_response(result)
            
            # Add metadata
            compatibility["processing_time"] = time.time() - start_time
            compatibility["ai_model_used"] = self._get_last_model_used()
            
            # Cache result
            if use_cache:
                await redis_client.set(
                    cache_key,
                    compatibility,
                    expire=3600  # 1 hour
                )
            
            logger.info(f"Compatibility analysis completed for user {user_id} in {compatibility['processing_time']:.2f}s")
            return compatibility
            
        except Exception as e:
            logger.error(f"Compatibility analysis failed for user {user_id}: {e}")
            raise AIServiceError(f"Failed to analyze compatibility: {str(e)}")
    
    async def _get_ai_response(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: str = "json",
        max_tokens: int = 4000
    ) -> str:
        """Get response from AI with fallback"""
        
        # Try Claude first
        if self.claude_client:
            try:
                response = await self._get_claude_response(
                    system_prompt, user_prompt, max_tokens
                )
                self._last_model_used = settings.CLAUDE_MODEL
                return response
            except Exception as e:
                logger.warning(f"Claude request failed: {e}, trying OpenAI fallback")
        
        # Fallback to OpenAI
        if self.openai_client:
            try:
                response = await self._get_openai_response(
                    system_prompt, user_prompt, response_format, max_tokens
                )
                self._last_model_used = settings.OPENAI_MODEL
                return response
            except Exception as e:
                logger.error(f"OpenAI request also failed: {e}")
                raise AIServiceError("All AI services are unavailable")
        
        raise AIServiceError("No AI services configured")
    
    async def _get_claude_response(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int
    ) -> str:
        """Get response from Claude"""
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await self.claude_client.messages.create(
                        model=settings.CLAUDE_MODEL,
                        max_tokens=max_tokens,
                        system=system_prompt,
                        messages=[
                            {"role": "user", "content": user_prompt}
                        ]
                    )
                
                return response.content[0].text
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise e
    
    async def _get_openai_response(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: str,
        max_tokens: int
    ) -> str:
        """Get response from OpenAI"""
        
        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Add JSON format instruction if needed
        if response_format == "json":
            messages.append({
                "role": "system", 
                "content": "Ответь строго в формате JSON как указано в промпте."
            })
        
        for attempt in range(self.max_retries):
            try:
                response = await self.openai_client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.7,
                    response_format={"type": "json_object"} if response_format == "json" else None
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise e
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse text analysis response"""
        try:
            data = safe_json_loads(response, {})
            toxicity_score = float(data.get("toxicity_score", 0))
            if not (0 <= toxicity_score <= 10):
                raise AIServiceError("toxicity_score вне диапазона 0-10")
            sentiment_score = data.get("sentiment_score")
            if sentiment_score is not None:
                sentiment_score = float(sentiment_score)
                if not (-1 <= sentiment_score <= 1):
                    raise AIServiceError("sentiment_score вне диапазона -1..1")
            return {
                "toxicity_score": toxicity_score,
                "urgency_level": data.get("urgency_level", "low"),
                "red_flags": data.get("red_flags", []),
                "patterns_detected": data.get("patterns_detected", []),
                "analysis": data.get("analysis", ""),
                "recommendation": data.get("recommendation", ""),
                "keywords": data.get("keywords", []),
                "confidence_score": float(data.get("confidence_score", 0.5)),
                "sentiment_score": sentiment_score,
            }
        except Exception as e:
            logger.error(f"Failed to parse analysis response: {e}")
            raise AIServiceError("Invalid response format from AI")
    
    def _parse_profile_response(self, response: str) -> Dict[str, Any]:
        """Parse partner profile response"""
        try:
            data = safe_json_loads(response, {})
            manipulation_risk = float(data.get("manipulation_risk", 5.0))
            if not (0 <= manipulation_risk <= 10):
                raise AIServiceError("manipulation_risk вне диапазона 0-10")
            overall_compatibility = data.get("overall_compatibility")
            if overall_compatibility is not None:
                overall_compatibility = float(overall_compatibility)
                if not (0 <= overall_compatibility <= 1):
                    raise AIServiceError("overall_compatibility вне диапазона 0-1")
            return {
                "personality_type": data.get("personality_type", ""),
                "manipulation_risk": manipulation_risk,
                "urgency_level": data.get("urgency_level", "medium"),
                "red_flags": data.get("red_flags", []),
                "positive_traits": data.get("positive_traits", []),
                "warning_signs": data.get("warning_signs", []),
                "psychological_profile": data.get("psychological_profile", ""),
                "relationship_advice": data.get("relationship_advice", ""),
                "communication_tips": data.get("communication_tips", ""),
                "trust_indicators": data.get("trust_indicators", []),
                "overall_compatibility": overall_compatibility,
            }
        except Exception as e:
            logger.error(f"Failed to parse profile response: {e}")
            raise AIServiceError("Invalid response format from AI")
    
    def _parse_compatibility_response(self, response: str) -> Dict[str, Any]:
        """Parse compatibility analysis response"""
        try:
            data = safe_json_loads(response, {})
            overall_compatibility = float(data.get("overall_compatibility", 5.0))
            if not (0 <= overall_compatibility <= 1):
                raise AIServiceError("overall_compatibility вне диапазона 0-1")
            return {
                "overall_compatibility": overall_compatibility,
                "communication_compatibility": float(data.get("communication_compatibility", 5.0)),
                "values_compatibility": float(data.get("values_compatibility", 5.0)),
                "lifestyle_compatibility": float(data.get("lifestyle_compatibility", 5.0)),
                "emotional_compatibility": float(data.get("emotional_compatibility", 5.0)),
                "similarity_score": float(data.get("similarity_score", 5.0)),
                "complement_score": float(data.get("complement_score", 5.0)),
                "conflict_potential": float(data.get("conflict_potential", 5.0)),
                "strengths": data.get("strengths", []),
                "challenges": data.get("challenges", []),
                "recommendations": data.get("recommendations", []),
                "compatibility_analysis": data.get("compatibility_analysis", ""),
                "relationship_advice": data.get("relationship_advice", ""),
                "growth_areas": data.get("growth_areas", "")
            }
        except Exception as e:
            logger.error(f"Failed to parse compatibility response: {e}")
            raise AIServiceError("Invalid response format from AI")
    
    async def _check_rate_limit(self, user_id: int) -> None:
        """Check rate limiting for user"""
        now = time.time()
        rate_limit = getattr(settings, 'AI_RATE_LIMIT_SECONDS', 3.0)
        # Simple rate limiting - max 1 request per N seconds per user
        if user_id in self._last_requests:
            time_since_last = now - self._last_requests[user_id]
            if time_since_last < rate_limit:
                wait_time = rate_limit - time_since_last
                await asyncio.sleep(wait_time)
        self._last_requests[user_id] = now
    
    def _get_last_model_used(self) -> str:
        """Get the last AI model used"""
        return getattr(self, '_last_model_used', 'unknown')
    
    def _create_fallback_analysis(self, answers: Dict[str, int]) -> Dict[str, Any]:
        """Create fallback analysis if AI fails"""
        from app.prompts.profiler_full_questions import calculate_weighted_scores, get_safety_alerts
        
        # Calculate weighted risk scores
        scores = calculate_weighted_scores(answers)
        safety_alerts = get_safety_alerts(answers)
        overall_risk = scores.get("overall_risk_score", 50.0)
        block_scores = scores.get("block_scores", {})
        
        # Determine urgency level
        if overall_risk >= 75.0:
            urgency = "CRITICAL"
            recommendations = [
                "🚨 КРИТИЧЕСКИЙ УРОВЕНЬ РИСКА - обратитесь за помощью немедленно",
                "Рассмотрите план безопасности",
                "Свяжитесь со службами помощи жертвам домашнего насилия"
            ]
        elif overall_risk >= 50.0:
            urgency = "HIGH"
            recommendations = [
                "Установите четкие границы в отношениях",
                "Рассмотрите консультацию психолога",
                "Обратитесь за поддержкой к близким"
            ]
        elif overall_risk >= 25.0:
            urgency = "MEDIUM" 
            recommendations = [
                "Работайте над улучшением коммуникации",
                "Обратите внимание на проблемные паттерны",
                "Рассмотрите парную терапию"
            ]
        else:
            urgency = "LOW"
            recommendations = [
                "Продолжайте развивать здоровые отношения",
                "Поддерживайте открытое общение",
                "Изучайте навыки эмоциональной поддержки"
            ]
        
        return {
            "overall_risk_score": overall_risk,
            "urgency_level": urgency,
            "block_scores": block_scores,
            "block_analysis": {
                "narcissism": {
                    "score": block_scores.get("narcissism", 0),
                    "level": self._risk_to_level(block_scores.get("narcissism", 0)),
                    "key_patterns": ["Анализ основан на базовых алгоритмах"],
                    "evidence": "Автоматический расчет на основе ответов"
                },
                "control": {
                    "score": block_scores.get("control", 0),
                    "level": self._risk_to_level(block_scores.get("control", 0)),
                    "key_patterns": ["Анализ основан на базовых алгоритмах"],
                    "evidence": "Автоматический расчет на основе ответов"
                },
                "gaslighting": {
                    "score": block_scores.get("gaslighting", 0),
                    "level": self._risk_to_level(block_scores.get("gaslighting", 0)),
                    "key_patterns": ["Анализ основан на базовых алгоритмах"],
                    "evidence": "Автоматический расчет на основе ответов"
                },
                "emotion": {
                    "score": block_scores.get("emotion", 0),
                    "level": self._risk_to_level(block_scores.get("emotion", 0)),
                    "key_patterns": ["Анализ основан на базовых алгоритмах"],
                    "evidence": "Автоматический расчет на основе ответов"
                },
                "intimacy": {
                    "score": block_scores.get("intimacy", 0),
                    "level": self._risk_to_level(block_scores.get("intimacy", 0)),
                    "key_patterns": ["Анализ основан на базовых алгоритмах"],
                    "evidence": "Автоматический расчет на основе ответов"
                },
                "social": {
                    "score": block_scores.get("social", 0),
                    "level": self._risk_to_level(block_scores.get("social", 0)),
                    "key_patterns": ["Анализ основан на базовых алгоритмах"],
                    "evidence": "Автоматический расчет на основе ответов"
                }
            },
            "psychological_profile": "Профиль создан с использованием научно обоснованных алгоритмов оценки рисков. Для более точного анализа рекомендуется консультация специалиста.",
            "risk_factors": ["Автоматический анализ - требует проверки специалистом"],
            "protective_factors": ["Обращение за помощью и проведение самоанализа"],
            "red_flags": safety_alerts if safety_alerts else [],
            "safety_alerts": safety_alerts,
            "immediate_recommendations": recommendations,
            "long_term_recommendations": [
                "Развивайте навыки здорового общения",
                "Изучайте признаки здоровых отношений",
                "Работайте над повышением самооценки"
            ],
            "communication_advice": [
                "Практикуйте открытое и честное общение",
                "Устанавливайте четкие личные границы",
                "Изучайте техники конструктивного разрешения конфликтов"
            ],
            "support_resources": [
                "Психологическая помощь: 8-800-2000-122",
                "Кризисная линия доверия: 8-800-7000-600",
                "Служба экстренного реагирования: 112"
            ],
            "relationship_prognosis": "Прогноз зависит от готовности партнеров работать над отношениями",
            "confidence_score": 0.7,
            "immediate_recommendations": recommendations,
            "analysis": f"АВТОМАТИЧЕСКИЙ АНАЛИЗ\n\nОбщий балл риска: {overall_risk}% ({urgency})\n\nЭтот анализ создан автоматически на основе ваших ответов. Для получения более детального заключения рекомендуется консультация квалифицированного специалиста."
        }
    
    def _risk_to_level(self, risk_score: float) -> str:
        """Convert risk score to text level"""
        if risk_score >= 8.0:
            return "критический"
        elif risk_score >= 6.0:
            return "высокий"
        elif risk_score >= 3.0:
            return "умеренный"
        else:
            return "низкий"
    
    def _validate_profiler_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize profiler AI response"""
        # Ensure required fields exist
        required_fields = [
            "overall_risk_score", "urgency_level", "block_analysis",
            "psychological_profile", "immediate_recommendations"
        ]
        
        for field in required_fields:
            if field not in response:
                logger.warning(f"Missing required field in AI response: {field}")
                if field == "overall_risk_score":
                    response[field] = 50.0
                elif field == "urgency_level":
                    response[field] = "MEDIUM"
                elif field == "block_analysis":
                    response[field] = {}
                else:
                    response[field] = []
        
        # Validate risk score range (0-100% for full version)
        if not isinstance(response["overall_risk_score"], (int, float)):
            response["overall_risk_score"] = 50.0
        else:
            response["overall_risk_score"] = max(0, min(100, float(response["overall_risk_score"])))
        
        # Validate urgency level
        valid_urgency_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        if response["urgency_level"] not in valid_urgency_levels:
            response["urgency_level"] = "MEDIUM"
        
        return response
    
    async def health_check(self) -> Dict[str, Any]:
        """Check AI service health"""
        status = {
            "claude_available": bool(self.claude_client),
            "openai_available": bool(self.openai_client),
            "services_configured": 0
        }
        
        if self.claude_client:
            status["services_configured"] += 1
            
        if self.openai_client:
            status["services_configured"] += 1
        
        status["status"] = "healthy" if status["services_configured"] > 0 else "unhealthy"
        
        return status

    def _create_full_fallback_analysis(self, answers: Dict[str, int], scores: Dict[str, Any], partner_name: str) -> Dict[str, Any]:
        """Create fallback analysis for full profiler when AI fails"""
        try:
            from app.prompts.profiler_full_questions import get_safety_alerts
            
            # Get safety alerts
            alerts = get_safety_alerts(answers)
            
            # Generate basic analysis based on scores
            block_scores = scores["block_scores"]
            overall_risk = scores["overall_risk_score"]
            urgency_level = scores["urgency_level"].value
            
            # Generate immediate recommendations
            immediate_recommendations = []
            if overall_risk >= 75:
                immediate_recommendations = [
                    "🚨 КРИТИЧЕСКИЙ УРОВЕНЬ РИСКА - обратитесь за профессиональной помощью немедленно",
                    "Рассмотрите план безопасности и возможность временного разъезда",
                    "Свяжитесь с службами помощи жертвам домашнего насилия"
                ]
            elif overall_risk >= 50:
                immediate_recommendations = [
                    "⚠️ Высокий уровень риска - рекомендуется консультация специалиста",
                    "Обсудите ситуацию с доверенными людьми",
                    "Изучите информацию о здоровых отношениях"
                ]
            else:
                immediate_recommendations = [
                    "Результаты указывают на относительно низкий риск",
                    "Продолжайте работать над улучшением отношений",
                    "При возникновении проблем обращайтесь к специалисту"
                ]
            
            # Create basic analysis text
            analysis_parts = [
                f"**АВТОМАТИЧЕСКИЙ АНАЛИЗ ПРОФИЛЯ: {partner_name}**\n",
                f"Общий балл риска: {overall_risk}% ({urgency_level})\n",
                "**АНАЛИЗ ПО БЛОКАМ:**"
            ]
            
            block_names = {
                "narcissism": "🧠 Нарциссизм и грандиозность",
                "control": "🎯 Контроль и манипуляции",
                "gaslighting": "🔄 Газлайтинг и искажение реальности",
                "emotion": "💭 Эмоциональная регуляция",
                "intimacy": "💕 Интимность и принуждение",
                "social": "👥 Социальное поведение"
            }
            
            for block, score in block_scores.items():
                block_name = block_names.get(block, block)
                risk_level = "ВЫСОКИЙ" if score >= 7 else "СРЕДНИЙ" if score >= 4 else "НИЗКИЙ"
                analysis_parts.append(f"- {block_name}: {score}/10 ({risk_level})")
            
            if alerts:
                analysis_parts.append("\n**ПРЕДУПРЕЖДЕНИЯ БЕЗОПАСНОСТИ:**")
                analysis_parts.extend([f"- {alert}" for alert in alerts])
            
            analysis_parts.append("\n**РЕКОМЕНДАЦИИ:**")
            analysis_parts.extend([f"- {rec}" for rec in immediate_recommendations])
            
            return {
                "analysis": "\n".join(analysis_parts),
                "block_scores": block_scores,
                "overall_risk_score": overall_risk,
                "urgency_level": urgency_level,
                "safety_alerts": alerts,
                "immediate_recommendations": immediate_recommendations,
                "partner_name": partner_name,
                "total_questions": 28,
                "questionnaire_version": "full_v1.0",
                "ai_available": False,
                "fallback_reason": "AI сервис недоступен - использован автоматический анализ",
                "created_at": time.time()
            }
            
        except Exception as e:
            logger.error(f"Full fallback analysis failed: {e}")
            return self._create_basic_fallback_analysis(answers, partner_name)

    def _create_basic_fallback_analysis(self, answers: Dict[str, int], partner_name: str) -> Dict[str, Any]:
        """Create basic fallback when everything else fails"""
        return {
            "analysis": f"**ОШИБКА АНАЛИЗА ПРОФИЛЯ: {partner_name}**\n\nК сожалению, не удалось проанализировать ваши ответы из-за технических проблем. Пожалуйста, обратитесь к специалисту для профессиональной оценки ситуации.",
            "block_scores": {},
            "overall_risk_score": 50.0,
            "urgency_level": "MEDIUM",
            "safety_alerts": [],
            "immediate_recommendations": [
                "Обратитесь к специалисту для профессиональной оценки",
                "Используйте контакты экстренной помощи при необходимости"
            ],
            "partner_name": partner_name,
            "total_questions": len(answers),
            "error": True,
            "fallback_reason": "Критическая ошибка системы",
            "emergency_contacts": [
                "112 - Служба экстренного реагирования", 
                "8-800-7000-600 - Национальная горячая линия"
            ],
            "created_at": time.time()
        }


# Global AI service instance
ai_service = AIService() 