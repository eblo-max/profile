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
        answers: Dict[int, str],
        user_id: int,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Create partner psychological profile
        
        Args:
            answers: Questionnaire answers
            user_id: User ID
            use_cache: Whether to use cache
            
        Returns:
            Profile analysis
        """
        start_time = time.time()
        
        # Create cache key
        answers_hash = hash(json.dumps(answers, sort_keys=True))
        cache_key = create_cache_key("partner_profile", user_id, answers_hash)
        
        # Try cache
        if use_cache:
            cached_result = await redis_client.get(cache_key)
            if cached_result:
                logger.info(f"Partner profile cache hit for user {user_id}")
                return cached_result
        
        # Check rate limiting
        await self._check_rate_limit(user_id)
        
        try:
            # Prepare prompt
            user_prompt = get_profiler_prompt(answers)
            
            # Get analysis from AI
            async with self._request_semaphore:
                result = await self._get_ai_response(
                    system_prompt=PROFILER_SYSTEM_PROMPT,
                    user_prompt=user_prompt,
                    response_format="json"
                )
            
            # Parse response
            profile = self._parse_profile_response(result)
            
            # Add metadata
            profile["processing_time"] = time.time() - start_time
            profile["ai_model_used"] = self._get_last_model_used()
            
            # Cache result
            if use_cache:
                await redis_client.set(
                    cache_key,
                    profile,
                    expire=3600  # 1 hour
                )
            
            logger.info(f"Partner profile completed for user {user_id} in {profile['processing_time']:.2f}s")
            return profile
            
        except Exception as e:
            logger.error(f"Partner profiling failed for user {user_id}: {e}")
            raise AIServiceError(f"Failed to profile partner: {str(e)}")
    
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


# Global AI service instance
ai_service = AIService() 