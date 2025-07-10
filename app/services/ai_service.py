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
from app.utils.helpers import safe_json_loads, create_cache_key, extract_json_from_text
from app.prompts.analysis_prompts import (
    ANALYSIS_SYSTEM_PROMPT,
    PROFILER_SYSTEM_PROMPT, 
    COMPATIBILITY_SYSTEM_PROMPT,
    get_text_analysis_prompt,
    get_profiler_prompt,
    get_compatibility_prompt,
    get_safe_advice_prompt,
    get_cot_text_analysis_prompt,
    get_tot_profiler_prompt,
    get_meta_prompt_generator,
    get_self_refining_prompt
)
from app.utils.enums import UrgencyLevel
import traceback


class ContextEngineer:
    """
    Context Engineering class for semantic field management and optimization
    """
    
    def __init__(self):
        self.field_state = {
            "attractors": [],
            "boundaries": {},
            "resonance": 0.0,
            "residue": [],
            "token_budget": 4000
        }
        
    def create_semantic_attractor(self, concept: str, strength: float = 0.8) -> dict:
        """Create a semantic attractor for context focus"""
        return {
            "concept": concept,
            "strength": strength,
            "embedding": None,  # Would be computed with actual embeddings
            "activation_count": 0
        }
    
    def establish_field_boundaries(self, relevance_threshold: float = 0.6) -> dict:
        """Establish semantic boundaries for information filtering"""
        return {
            "permeability": 0.7,
            "gradient": 0.2,
            "relevance_threshold": relevance_threshold,
            "filter_criteria": ["clinical_relevance", "safety_importance", "practical_utility"]
        }
    
    def optimize_context_for_budget(self, context: str, target_tokens: int) -> str:
        """Optimize context to fit token budget using field-aware methods"""
        # Simplified token counting (in real implementation would use proper tokenizer)
        current_tokens = len(context.split()) * 1.3  # Rough approximation
        
        if current_tokens <= target_tokens:
            return context
        
        # Field-aware compression
        if self.field_state["attractors"]:
            # Prioritize content related to attractors
            paragraphs = context.split("\n\n")
            
            # Score paragraphs by relevance to attractors
            scored_paragraphs = []
            for paragraph in paragraphs:
                relevance_score = self._calculate_attractor_relevance(paragraph)
                paragraph_tokens = len(paragraph.split()) * 1.3
                scored_paragraphs.append((paragraph, relevance_score, paragraph_tokens))
            
            # Sort by relevance and add until budget is reached
            scored_paragraphs.sort(key=lambda x: x[1], reverse=True)
            
            optimized_content = []
            used_tokens = 0
            
            for paragraph, score, tokens in scored_paragraphs:
                if used_tokens + tokens <= target_tokens:
                    optimized_content.append(paragraph)
                    used_tokens += tokens
                else:
                    break
            
            return "\n\n".join(optimized_content)
        
        # Fallback: simple truncation
        ratio = target_tokens / current_tokens
        return context[:int(len(context) * ratio)]
    
    def _calculate_attractor_relevance(self, text: str) -> float:
        """Calculate relevance of text to current attractors"""
        if not self.field_state["attractors"]:
            return 0.5
        
        # Simplified relevance calculation
        relevance_scores = []
        text_lower = text.lower()
        
        for attractor in self.field_state["attractors"]:
            concept = attractor["concept"].lower()
            if concept in text_lower:
                relevance_scores.append(attractor["strength"])
            else:
                # Simple word overlap scoring
                concept_words = set(concept.split())
                text_words = set(text_lower.split())
                overlap = len(concept_words.intersection(text_words))
                if overlap > 0:
                    relevance_scores.append(overlap / len(concept_words) * attractor["strength"])
        
        return max(relevance_scores) if relevance_scores else 0.1
    
    def amplify_resonance(self, concepts: list) -> dict:
        """Amplify resonance between compatible concepts"""
        resonance_patterns = {}
        
        for i, concept1 in enumerate(concepts):
            for j, concept2 in enumerate(concepts[i+1:], i+1):
                # Calculate conceptual resonance (simplified)
                resonance_score = self._calculate_concept_resonance(concept1, concept2)
                if resonance_score > 0.5:
                    resonance_patterns[f"{concept1}-{concept2}"] = resonance_score
        
        self.field_state["resonance"] = sum(resonance_patterns.values()) / len(resonance_patterns) if resonance_patterns else 0.0
        return resonance_patterns
    
    def _calculate_concept_resonance(self, concept1: str, concept2: str) -> float:
        """Calculate resonance between two concepts"""
        # Simplified resonance calculation
        # In real implementation, would use semantic embeddings
        
        # Define known resonant pairs for psychology domain
        resonant_pairs = {
            ("control", "manipulation"): 0.9,
            ("gaslighting", "emotional_abuse"): 0.8,
            ("isolation", "social_control"): 0.85,
            ("threats", "intimidation"): 0.9,
            ("narcissism", "lack_of_empathy"): 0.8
        }
        
        pair = tuple(sorted([concept1.lower(), concept2.lower()]))
        return resonant_pairs.get(pair, 0.3)
    
    def preserve_residue(self, key_concepts: list) -> None:
        """Preserve critical information across context changes"""
        self.field_state["residue"] = key_concepts
    
    def create_field_aware_prompt(self, base_prompt: str, task_context: str) -> str:
        """Create a field-aware prompt with semantic optimization"""
        
        # Identify key concepts for attractors
        key_concepts = self._extract_key_concepts(task_context)
        
        # Create semantic attractors
        self.field_state["attractors"] = [
            self.create_semantic_attractor(concept, 0.8) 
            for concept in key_concepts[:3]  # Limit to top 3
        ]
        
        # Establish boundaries
        self.field_state["boundaries"] = self.establish_field_boundaries()
        
        # Optimize prompt for token budget
        optimized_prompt = self.optimize_context_for_budget(
            base_prompt, 
            self.field_state["token_budget"] * 0.7  # Reserve 30% for response
        )
        
        # Add field management instructions
        field_instructions = self._generate_field_instructions()
        
        return f"{optimized_prompt}\n\n{field_instructions}"
    
    def _extract_key_concepts(self, context: str) -> list:
        """Extract key concepts from context for attractor creation"""
        # Simplified concept extraction
        psychology_keywords = [
            "manipulation", "control", "gaslighting", "emotional_abuse",
            "narcissism", "isolation", "threats", "intimidation",
            "safety", "risk_assessment", "behavioral_patterns"
        ]
        
        context_lower = context.lower()
        found_concepts = [
            keyword for keyword in psychology_keywords 
            if keyword in context_lower
        ]
        
        return found_concepts[:5]  # Return top 5 concepts
    
    def _generate_field_instructions(self) -> str:
        """Generate field management instructions for the prompt"""
        
        attractors_text = ", ".join([a["concept"] for a in self.field_state["attractors"]])
        
        return f"""
<field_management>
CORE ATTRACTORS: {attractors_text}
- Поддерживай фокус на этих концепциях
- Включай релевантную информацию с приоритетом

BOUNDARY RULES:
- Включай новую информацию только при релевантности > 7/10
- Поддерживай согласованность с предыдущим контекстом
- Фильтруй касательную информацию

RESIDUE PRESERVATION:
- Ключевые определения должны сохраняться
- Критические решения/выводы должны быть сохранены
- Основные принципы должны подкрепляться

OPTIMIZATION DIRECTIVES:
- Приоритизируй контент с высокой релевантностью к основным аттракторам
- Сжимай формат, но сохраняй смысл
- Поддерживай клиническую точность
</field_management>
"""


class CognitiveTools:
    """
    Specialized cognitive tools for complex reasoning tasks
    """
    
    @staticmethod
    def recursive_analysis(question: str, iterations: int = 2) -> str:
        """Apply recursive analysis for improved responses"""
        
        return f"""
<recursive_analysis>
Проведи {iterations} итерации анализа для улучшения качества ответа:

ИТЕРАЦИЯ 1: Первичный анализ
{question}

САМОПРОВЕРКА 1:
1. Какая информация может отсутствовать?
2. Есть ли предположения, которые следует поставить под сомнение?
3. Как можно сделать объяснение более четким или точным?

ИТЕРАЦИЯ 2: Улучшенный анализ
На основе самопроверки, предоставь улучшенный ответ:

ФИНАЛЬНАЯ ПРОВЕРКА:
- Достаточно ли полон анализ?
- Соответствуют ли выводы доказательствам?
- Практичны ли рекомендации?
</recursive_analysis>
"""
    
    @staticmethod
    def multi_perspective_analysis(question: str, perspectives: list) -> str:
        """Analyze from multiple expert perspectives"""
        
        perspectives_text = "\n".join([
            f"ПЕРСПЕКТИВА {i+1}: {perspective}" 
            for i, perspective in enumerate(perspectives)
        ])
        
        return f"""
<multi_perspective_analysis>
Проанализируй следующий вопрос с разных экспертных позиций:

ВОПРОС: {question}

{perspectives_text}

СИНТЕЗ ПЕРСПЕКТИВ:
1. Найди общие темы и согласованные выводы
2. Выяви различия в подходах и интерпретациях
3. Определи наиболее обоснованную позицию
4. Сформулируй комплексное заключение
</multi_perspective_analysis>
"""


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
        
        # Advanced Prompt Engineering components
        self.context_engineer = ContextEngineer()
        self.cognitive_tools = CognitiveTools()
        
        # Prompt technique selection
        self.prompt_techniques = {
            "chain_of_thought": "cot",
            "tree_of_thoughts": "tot",
            "meta_prompting": "meta",
            "self_refining": "refine",
            "field_aware": "field"
        }
    
    async def analyze_text_advanced(
        self,
        text: str,
        user_id: int,
        context: str = "",
        technique: str = "chain_of_thought",
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Advanced text analysis using specified prompting technique
        """
        start_time = time.time()
        
        # Create cache key including technique
        cache_key = create_cache_key("text_analysis_advanced", user_id, hash(text + context + technique))
        
        # Try cache
        if use_cache:
            cached_result = await redis_client.get(cache_key)
            if cached_result:
                logger.info(f"Advanced text analysis cache hit for user {user_id} with {technique}")
                return cached_result
        
        # Check rate limiting
        await self._check_rate_limit(user_id)
        
        try:
            # Select prompting technique
            if technique == "chain_of_thought":
                user_prompt = get_cot_text_analysis_prompt(text, context)
                system_prompt = ANALYSIS_SYSTEM_PROMPT
                
            elif technique == "meta_prompting":
                # First generate optimized prompt
                meta_prompt = get_meta_prompt_generator("text_analysis", "advanced", "psychology")
                meta_result = await self._get_ai_response(
                    system_prompt="Ты эксперт по prompt engineering",
                    user_prompt=meta_prompt,
                    response_format="json"
                )
                
                # Extract optimized prompt
                meta_response = extract_json_from_text(meta_result)
                optimized_prompt = meta_response.get("optimized_prompt", get_cot_text_analysis_prompt(text, context))
                
                user_prompt = optimized_prompt.format(text=text, context=context)
                system_prompt = ANALYSIS_SYSTEM_PROMPT
                
            elif technique == "field_aware":
                # Use context engineering
                base_prompt = get_text_analysis_prompt(text, context)
                user_prompt = self.context_engineer.create_field_aware_prompt(
                    base_prompt, 
                    f"text_analysis: {text[:200]}"  # First 200 chars for context
                )
                system_prompt = ANALYSIS_SYSTEM_PROMPT
                
            else:
                # Fallback to standard
                user_prompt = get_text_analysis_prompt(text, context)
                system_prompt = ANALYSIS_SYSTEM_PROMPT
            
            # Get analysis from AI
            async with self._request_semaphore:
                result = await self._get_ai_response_with_quality_check(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    response_format="json",
                    max_tokens=5000,
                    min_quality_score=75
                )
            
            # Parse and validate response
            analysis = self._parse_analysis_response(result)
            
            # Apply self-refining if requested
            if technique == "self_refining":
                refining_prompt = get_self_refining_prompt(
                    json.dumps(analysis, ensure_ascii=False), 
                    f"Анализ текста: {text[:100]}..."
                )
                
                refined_result = await self._get_ai_response(
                    system_prompt="Ты эксперт по улучшению AI ответов",
                    user_prompt=refining_prompt,
                    response_format="json"
                )
                
                refined_response = extract_json_from_text(refined_result)
                if "refined_response" in refined_response:
                    analysis = extract_json_from_text(refined_response["refined_response"])
            
            # Validate response quality
            analysis = self._validate_response_quality(analysis, 'analysis')
            
            # Add metadata
            analysis["processing_time"] = time.time() - start_time
            analysis["ai_model_used"] = self._get_last_model_used()
            analysis["technique_used"] = technique
            
            # Log performance metrics
            self._log_performance_metrics(analysis, f'text_analysis_{technique}', analysis["processing_time"])
            
            # Cache result
            if use_cache:
                await redis_client.set(cache_key, analysis, expire=1800)
            
            logger.info(f"Advanced text analysis completed for user {user_id} using {technique} in {analysis['processing_time']:.2f}s")
            return analysis
            
        except Exception as e:
            logger.error(f"Advanced text analysis failed for user {user_id}: {e}")
            raise AIServiceError(f"Failed to analyze text with {technique}: {str(e)}")
    
    async def profile_partner_advanced(
        self,
        answers: List[Dict[str, Any]],
        user_id: int,
        partner_name: str = "партнер",
        partner_description: str = "",
        technique: str = "tree_of_thoughts",
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Advanced partner profiling using specified technique
        """
        start_time = time.time()
        
        # Convert answers format
        if isinstance(answers, list):
            answers_text = []
            for answer in answers:
                question_text = answer.get('question', f"Question {answer.get('question_id', 'N/A')}")
                answer_text = answer.get('answer', 'No answer')
                answers_text.append(f"Q: {question_text}\nA: {answer_text}")
            combined_answers = "\n\n".join(answers_text)
        else:
            combined_answers = str(answers)
        
        # Create cache key
        cache_key = create_cache_key("profile_advanced", user_id, hash(combined_answers + partner_name + technique))
        
        # Try cache
        if use_cache:
            cached_result = await redis_client.get(cache_key)
            if cached_result:
                logger.info(f"Advanced profile cache hit for user {user_id} with {technique}")
                return cached_result
        
        # Check rate limiting
        await self._check_rate_limit(user_id)
        
        try:
            # Format answers for AI analysis
            answers_text = ""
            for i, answer in enumerate(answers, 1):
                question = answer.get('question', f'Вопрос {i}')
                answer_text = answer.get('answer', 'Нет ответа')
                answers_text += f"{i}. {question}\n   Ответ: {answer_text}\n\n"
            
            # Select prompting technique
            if technique == "tree_of_thoughts":
                user_prompt = get_tot_profiler_prompt(answers_text, partner_name, partner_description)
                system_prompt = PROFILER_SYSTEM_PROMPT
                max_tokens = 8000  # ToT needs more space
                
            elif technique == "cognitive_tools":
                # Use recursive analysis
                base_question = f"Проанализируй профиль партнера на основе ответов: {answers_text[:500]}..."
                recursive_prompt = self.cognitive_tools.recursive_analysis(base_question, iterations=3)
                user_prompt = f"{get_profiler_prompt(answers_text, partner_name, partner_description)}\n\n{recursive_prompt}"
                system_prompt = PROFILER_SYSTEM_PROMPT
                max_tokens = 7000
                
            elif technique == "multi_perspective":
                # Multi-perspective analysis
                perspectives = [
                    "Клинический психолог со специализацией на расстройствах личности",
                    "Специалист по домашнему насилию и безопасности",
                    "Семейный терапевт с опытом работы с парами"
                ]
                base_question = f"Оцени риски в отношениях на основе: {answers_text[:300]}..."
                multi_perspective_prompt = self.cognitive_tools.multi_perspective_analysis(base_question, perspectives)
                user_prompt = f"{get_profiler_prompt(answers_text, partner_name, partner_description)}\n\n{multi_perspective_prompt}"
                system_prompt = PROFILER_SYSTEM_PROMPT
                max_tokens = 7000
                
            else:
                # Standard profiling
                user_prompt = get_profiler_prompt(answers_text, partner_name, partner_description)
                system_prompt = PROFILER_SYSTEM_PROMPT
                max_tokens = 6000
            
            # Get analysis from AI
            async with self._request_semaphore:
                result = await self._get_ai_response_with_quality_check(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    response_format="json",
                    max_tokens=max_tokens,
                    min_quality_score=80
                )
            
            # Parse and validate response
            if technique == "tree_of_thoughts":
                profile = self._parse_tot_profile_response(result)
            else:
                profile = self._parse_profile_response(result)
                
            profile = self._validate_profiler_response(profile)
            
            # Add metadata
            profile["processing_time"] = time.time() - start_time
            profile["ai_model_used"] = self._get_last_model_used()
            profile["technique_used"] = technique
            
            # Log performance metrics
            self._log_performance_metrics(profile, f'profiler_{technique}', profile["processing_time"])
            
            # Cache result
            if use_cache:
                await redis_client.set(cache_key, profile, expire=3600)
            
            logger.info(f"Advanced profiling completed for user {user_id} using {technique} in {profile['processing_time']:.2f}s")
            return profile
            
        except Exception as e:
            logger.error(f"Advanced profiling failed for user {user_id}: {e}")
            raise AIServiceError(f"Failed to profile partner with {technique}: {str(e)}")
    
    # Backward compatibility methods
    async def analyze_text(
        self,
        text: str,
        user_id: int,
        context: str = "",
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Backward compatible text analysis (uses Chain-of-Thought by default)
        """
        return await self.analyze_text_advanced(
            text=text,
            user_id=user_id,
            context=context,
            technique="chain_of_thought",
            use_cache=use_cache
        )
    
    async def profile_partner(
        self,
        answers: List[Dict[str, Any]],
        user_id: int,
        partner_name: str = "партнер",
        partner_description: str = "",
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Backward compatible partner profiling (uses Tree-of-Thoughts by default)
        """
        try:
            return await self.profile_partner_advanced(
                answers=answers,
                user_id=user_id,
                partner_name=partner_name,
                partner_description=partner_description,
                technique="tree_of_thoughts",
                use_cache=use_cache
            )
        except Exception as e:
            logger.error(f"Advanced profiling failed, falling back to basic analysis: {e}")
            # Fallback to basic analysis if advanced fails
            try:
                from app.prompts.profiler_full_questions import calculate_weighted_scores
                scores = calculate_weighted_scores(answers)
                return self._create_full_fallback_analysis(answers, scores, partner_name)
            except Exception as fallback_error:
                logger.error(f"Fallback analysis also failed: {fallback_error}")
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
            
            # Validate response quality
            compatibility = self._validate_response_quality(compatibility, 'compatibility')
            
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
    
    async def _get_ai_response_with_quality_check(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: str = "json",
        max_tokens: int = 4000,
        min_quality_score: int = 70,
        max_retries: int = 2
    ) -> str:
        """
        Get AI response with quality validation and retry mechanism
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            response_format: Response format
            max_tokens: Maximum tokens
            min_quality_score: Minimum quality score to accept
            max_retries: Maximum retry attempts
            
        Returns:
            AI response string
        """
        for attempt in range(max_retries + 1):
            try:
                # Get AI response
                response = await self._get_ai_response(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    response_format=response_format,
                    max_tokens=max_tokens
                )
                
                # For first attempt, return immediately
                if attempt == 0:
                    return response
                
                # For retry attempts, check quality
                try:
                    # Quick quality check - parse response
                    if response_format == "json":
                        parsed = extract_json_from_text(response)
                        if parsed and len(parsed) >= 3:  # Basic structure check
                            return response
                except:
                    pass
                
                # If quality check fails, continue to next attempt
                logger.warning(f"AI response quality check failed, attempt {attempt + 1}/{max_retries + 1}")
                
            except Exception as e:
                logger.error(f"AI response attempt {attempt + 1} failed: {e}")
                if attempt == max_retries:
                    raise
                
                # Wait before retry
                await asyncio.sleep(1)
        
        return response  # Return last attempt even if quality is low
    
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
            # Try to extract JSON from structured response
            data = extract_json_from_text(response)
            if not data:
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
        """Parse partner profile response from AI"""
        try:
            # Try to extract JSON from structured response
            data = extract_json_from_text(response)
            if not data:
                data = safe_json_loads(response, {})
            
            # Extract main fields with fallbacks
            psychological_profile = data.get("psychological_profile", "")
            if not psychological_profile:
                # Try alternative keys
                psychological_profile = data.get("analysis", data.get("detailed_analysis", ""))
            
            red_flags = data.get("red_flags", [])
            if not red_flags:
                red_flags = data.get("warning_signs", [])
            
            survival_guide = data.get("survival_guide", [])
            if not survival_guide:
                survival_guide = data.get("recommendations", [])
            
            # Extract risk assessment
            risk_score = float(data.get("manipulation_risk", data.get("overall_risk_score", 5.0)))
            if risk_score > 10:
                risk_score = risk_score / 10  # Normalize if needed
            risk_score = min(10, max(0, risk_score)) * 10  # Scale to 0-100
            
            urgency = data.get("urgency_level", "medium").upper()
            
            # Extract Dark Triad scores
            dark_triad = data.get("dark_triad", {})
            if not dark_triad:
                # Calculate based on risk score
                dark_triad = {
                    "narcissism": min(10, risk_score / 10),
                    "machiavellianism": min(10, (risk_score - 5) / 10),
                    "psychopathy": min(10, (risk_score - 10) / 10)
                }
            
            # Extract block scores
            block_scores = data.get("block_scores", {})
            if not block_scores:
                # Generate based on risk score
                block_scores = {
                    "narcissism": min(10, risk_score / 12),
                    "control": min(10, risk_score / 10),
                    "gaslighting": min(10, (risk_score - 5) / 12),
                    "emotion": min(10, risk_score / 15),
                    "intimacy": min(10, (risk_score - 10) / 12),
                    "social": min(10, risk_score / 11)
                }
            
            return {
                "psychological_profile": psychological_profile,
                "red_flags": red_flags if isinstance(red_flags, list) else [red_flags],
                "survival_guide": survival_guide if isinstance(survival_guide, list) else [survival_guide],
                "dark_triad": dark_triad,
                "block_scores": block_scores,
                "overall_risk_score": risk_score,
                "urgency_level": urgency,
                "safety_alerts": data.get("safety_alerts", ["Рекомендуется консультация с психологом"]),
                "personality_type": data.get("personality_type", ""),
                "emotional_portrait": data.get("emotional_portrait", ""),
                "relationship_dynamics": data.get("relationship_dynamics", ""),
                "danger_assessment": data.get("danger_assessment", ""),
                "motivations": data.get("motivations", ""),
                "relationship_forecast": data.get("relationship_forecast", ""),
                "exit_strategy": data.get("exit_strategy", ""),
                "trust_indicators": data.get("trust_indicators", []),
                "ai_available": True,
                "fallback_used": False
            }
            
        except Exception as e:
            logger.error(f"Failed to parse profile response: {e}")
            logger.error(f"Response was: {response[:500]}...")
            raise AIServiceError(f"Failed to parse AI response: {str(e)}")
    
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
        """Validate and clean profiler response"""
        
        # Required fields with defaults
        required_fields = {
            "psychological_profile": "Анализ недоступен",
            "red_flags": [],
            "survival_guide": [],
            "overall_risk_score": 50.0,
            "urgency_level": "MEDIUM",
            "block_scores": {},
            "dark_triad": {},
            "safety_alerts": ["Рекомендуется консультация с психологом"]
        }
        
        # Ensure all required fields exist
        for field, default_value in required_fields.items():
            if field not in response:
                response[field] = default_value
                logger.warning(f"Missing field '{field}' in AI response, using default")
        
        # Validate and normalize risk score
        try:
            risk_score = float(response.get("overall_risk_score", 50.0))
            response["overall_risk_score"] = max(0, min(100, risk_score))
        except (ValueError, TypeError):
            response["overall_risk_score"] = 50.0
        
        # Validate urgency level
        valid_urgency = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        if response.get("urgency_level", "").upper() not in valid_urgency:
            response["urgency_level"] = "MEDIUM"
        
        # Ensure lists are actually lists
        list_fields = ["red_flags", "survival_guide", "safety_alerts", "trust_indicators"]
        for field in list_fields:
            if field in response and not isinstance(response[field], list):
                response[field] = [response[field]] if response[field] else []
        
        # Validate block scores
        if not isinstance(response.get("block_scores"), dict):
            response["block_scores"] = {}
        
        # Validate dark triad
        if not isinstance(response.get("dark_triad"), dict):
            response["dark_triad"] = {}
        
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

    def _parse_tot_profile_response(self, response: str) -> Dict[str, Any]:
        """Parse Tree of Thoughts profile response"""
        try:
            # Extract JSON from response
            profile_data = extract_json_from_text(response)
            
            if not profile_data:
                raise ValueError("No valid JSON found in ToT response")
            
            # Handle Tree of Thoughts specific structure
            if "consensus_analysis" in profile_data:
                consensus = profile_data["consensus_analysis"]
                expert_analyses = profile_data.get("expert_analyses", {})
                
                # Extract core information from consensus
                result = {
                    "personality_type": consensus.get("personality_type", "Неопределен"),
                    "manipulation_risk": consensus.get("manipulation_risk", 5),
                    "urgency_level": consensus.get("urgency_level", "medium"),
                    "psychological_profile": consensus.get("psychological_profile", "Профиль недоступен"),
                    "red_flags": consensus.get("red_flags", []),
                    "safety_alerts": consensus.get("safety_alerts", []),
                    "block_scores": profile_data.get("block_scores", {}),
                    "expert_agreement": consensus.get("expert_agreement", 0.5),
                    "expert_analyses": expert_analyses
                }
                
                # Add additional fields for compatibility
                result.update({
                    "positive_traits": [],
                    "danger_assessment": f"Согласованная оценка экспертов: {consensus.get('urgency_level', 'medium')}",
                    "relationship_forecast": "Основано на экспертном консенсусе",
                    "exit_strategy": "См. рекомендации по безопасности",
                    "confidence_level": consensus.get("expert_agreement", 0.5)
                })
                
                return result
            else:
                # Fallback to standard parsing
                return self._parse_profile_response(response)
                
        except Exception as e:
            logger.error(f"Failed to parse ToT profile response: {e}")
            # Fallback to standard parsing
            return self._parse_profile_response(response)

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

    def _create_basic_fallback_analysis(self, answers: List[Dict[str, Any]], partner_name: str) -> Dict[str, Any]:
        """Create basic fallback analysis when AI fails"""
        
        # Analyze answers for content
        answer_texts = []
        for answer in answers:
            answer_text = answer.get('answer', '').lower()
            answer_texts.append(answer_text)
        
        combined_text = ' '.join(answer_texts)
        
        # Determine risk level based on keywords
        high_risk_keywords = ['всегда', 'постоянно', 'никогда', 'запрещает', 'контролирует', 'кричит', 'злится', 'бьет', 'угрожает', 'изолирует']
        medium_risk_keywords = ['часто', 'иногда', 'может', 'бывает', 'не разрешает', 'ревнует', 'проверяет']
        
        high_risk_count = sum(1 for keyword in high_risk_keywords if keyword in combined_text)
        medium_risk_count = sum(1 for keyword in medium_risk_keywords if keyword in combined_text)
        
        if high_risk_count >= 3:
            risk_score = 85.0
            urgency = "CRITICAL"
        elif high_risk_count >= 1 or medium_risk_count >= 3:
            risk_score = 70.0
            urgency = "HIGH"
        elif medium_risk_count >= 1:
            risk_score = 55.0
            urgency = "MEDIUM"
        else:
            risk_score = 30.0
            urgency = "LOW"
        
        # Generate personalized psychological profile
        profile_parts = []
        
        if 'контролирует' in combined_text or 'проверяет' in combined_text:
            profile_parts.append(f"{partner_name} демонстрирует выраженные контролирующие тенденции. Он стремится управлять поведением партнера, ограничивая его автономию и свободу выбора.")
        
        if 'кричит' in combined_text or 'злится' in combined_text:
            profile_parts.append("Наблюдается эмоциональная нестабильность с вспышками гнева. Это может указывать на проблемы с регуляцией эмоций и склонность к агрессивному поведению.")
        
        if 'запрещает' in combined_text or 'не разрешает' in combined_text:
            profile_parts.append("Партнер пытается ограничить социальные контакты и личную свободу. Это классический признак изолирующего поведения, характерного для абьюзивных отношений.")
        
        if 'никогда' in combined_text and ('извиняется' in combined_text or 'признает' in combined_text):
            profile_parts.append("Отсутствие способности к признанию ошибок и извинениям указывает на нарциссические черты личности и проблемы с эмпатией.")
        
        if not profile_parts:
            profile_parts.append(f"На основе предоставленных ответов, {partner_name} демонстрирует некоторые проблемные паттерны поведения, которые требуют внимания и возможной коррекции.")
        
        psychological_profile = " ".join(profile_parts)
        
        # Generate red flags based on answers
        red_flags = []
        if 'контролирует' in combined_text:
            red_flags.append("Систематический контроль поведения и действий партнера")
        if 'проверяет телефон' in combined_text or 'проверяет сообщения' in combined_text:
            red_flags.append("Нарушение приватности и личных границ")
        if 'не разрешает' in combined_text or 'запрещает' in combined_text:
            red_flags.append("Ограничение социальных контактов и изоляция от близких")
        if 'кричит' in combined_text or 'злится' in combined_text:
            red_flags.append("Эмоциональная агрессия и вспышки гнева")
        if 'унижает' in combined_text or 'оскорбляет' in combined_text:
            red_flags.append("Эмоциональное насилие и унижение достоинства")
        
        if not red_flags:
            red_flags = ["Обнаружены признаки проблемного поведения, требующие внимания"]
        
        # Generate survival guide
        survival_guide = []
        if risk_score >= 70:
            survival_guide.extend([
                "Немедленно обратитесь к психологу или специалисту по семейным отношениям",
                "Создайте план безопасности и определите людей, к которым можно обратиться за помощью",
                "Восстановите связи с семьей и друзьями, которые могут оказать поддержку",
                "Изучите техники установления границ и защиты от манипуляций"
            ])
        else:
            survival_guide.extend([
                "Обратитесь к семейному психологу для работы с парой",
                "Изучите литературу о здоровых отношениях и коммуникации",
                "Практикуйте открытое и честное общение с партнером",
                "Установите четкие границы в отношениях"
            ])
        
        return {
            "psychological_profile": psychological_profile,
            "red_flags": red_flags,
            "survival_guide": survival_guide,
            "dark_triad": {
                "narcissism": min(10, risk_score / 10),
                "machiavellianism": min(10, (risk_score - 10) / 10),
                "psychopathy": min(10, (risk_score - 20) / 10)
            },
            "block_scores": {
                "narcissism": min(10, risk_score / 12),
                "control": min(10, risk_score / 10),
                "gaslighting": min(10, (risk_score - 5) / 12),
                "emotion": min(10, risk_score / 15),
                "intimacy": min(10, (risk_score - 10) / 12),
                "social": min(10, risk_score / 11)
            },
            "overall_risk_score": risk_score,
            "urgency_level": urgency,
            "safety_alerts": ["Рекомендуется консультация с психологом"],
            "partner_name": partner_name,
            "ai_available": False,
            "fallback_used": True
        }

    def _validate_response_quality(self, response: Dict[str, Any], response_type: str) -> Dict[str, Any]:
        """
        Validate AI response quality and completeness
        
        Args:
            response: AI response dictionary
            response_type: Type of response ('profile' or 'analysis')
            
        Returns:
            Updated response with quality metrics
        """
        quality_score = 0
        quality_issues = []
        
        if response_type == 'profile':
            # Check required fields
            required_fields = ['personality_type', 'psychological_profile', 'red_flags', 'manipulation_risk']
            for field in required_fields:
                if field in response and response[field]:
                    quality_score += 20
                else:
                    quality_issues.append(f"Missing or empty field: {field}")
            
            # Check psychological profile length
            profile_text = response.get('psychological_profile', '')
            if len(profile_text) >= 200:
                quality_score += 10
            else:
                quality_issues.append(f"Psychological profile too short: {len(profile_text)} chars")
            
            # Check red flags specificity
            red_flags = response.get('red_flags', [])
            if isinstance(red_flags, list) and len(red_flags) >= 3:
                quality_score += 10
            else:
                quality_issues.append(f"Insufficient red flags: {len(red_flags) if isinstance(red_flags, list) else 0}")
            
        elif response_type == 'analysis':
            # Check required fields for text analysis
            required_fields = ['toxicity_score', 'urgency_level', 'analysis', 'patterns_detected']
            for field in required_fields:
                if field in response and response[field]:
                    quality_score += 20
                else:
                    quality_issues.append(f"Missing or empty field: {field}")
            
            # Check toxicity-urgency alignment
            toxicity = response.get('toxicity_score', 0)
            urgency = response.get('urgency_level', 'low')
            
            urgency_mapping = {
                'low': (0, 3),
                'medium': (4, 6),
                'high': (7, 8),
                'critical': (9, 10)
            }
            
            expected_range = urgency_mapping.get(urgency, (0, 10))
            if expected_range[0] <= toxicity <= expected_range[1]:
                quality_score += 20
            else:
                quality_issues.append(f"Toxicity-urgency mismatch: {toxicity} vs {urgency}")
        
        # Add quality metrics to response
        response['quality_score'] = quality_score
        response['quality_issues'] = quality_issues
        response['quality_grade'] = self._get_quality_grade(quality_score)
        
        return response
    
    def _get_quality_grade(self, score: int) -> str:
        """Convert quality score to grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _log_performance_metrics(self, response: Dict[str, Any], response_type: str, processing_time: float):
        """
        Log performance metrics for monitoring
        
        Args:
            response: AI response
            response_type: Type of response
            processing_time: Processing time in seconds
        """
        quality_score = response.get('quality_score', 0)
        quality_grade = response.get('quality_grade', 'F')
        
        logger.info(f"AI Performance - Type: {response_type}, "
                   f"Quality: {quality_score}% ({quality_grade}), "
                   f"Time: {processing_time:.2f}s, "
                   f"Model: {self._get_last_model_used()}")
        
        # Log quality issues if any
        quality_issues = response.get('quality_issues', [])
        if quality_issues:
            logger.warning(f"Quality issues detected: {quality_issues}")


# Global AI service instance
ai_service = AIService() 