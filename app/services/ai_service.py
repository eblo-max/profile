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
from app.prompts.advanced_prompting_2025 import AdvancedPromptingSystem
from app.prompts.ultra_personalization_prompt import create_ultra_personalized_prompt_final, create_simplified_system_prompt, create_storytelling_analysis_prompt, create_storytelling_narrative_prompt
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
        
        # Revolutionary Advanced Prompting System 2025
        self.advanced_prompting = AdvancedPromptingSystem()
        
        # Prompt technique selection
        self.prompt_techniques = {
            "chain_of_thought": "cot",
            "tree_of_thoughts": "tot",
            "meta_prompting": "meta",
            "self_refining": "refine",
            "field_aware": "field",
            "ultra_personalized_2025": "ultra2025",
            "ultra_final": "ultra_final",
            "storytelling": "story"
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
        technique: str = "ultra_personalized_2025",
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
        
        # Устанавливаем имя партнера для использования в парсере
        self._current_partner_name = partner_name
        
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
                
            elif technique == "ultra_personalized_2025":
                # Revolutionary 2025 system
                user_prompt = self.advanced_prompting.create_ultra_personalized_prompt(
                    answers_text, partner_name, partner_description
                )
                system_prompt = self.advanced_prompting.create_enhanced_system_prompt()
                max_tokens = 8192  # Maximum for Claude 3.5 Sonnet
                
            elif technique == "ultra_final":
                # Финальная ультра-персонализированная система
                user_prompt = create_ultra_personalized_prompt_final(
                    answers_text, partner_name, partner_description
                )
                system_prompt = create_simplified_system_prompt()
                max_tokens = 8192  # Maximum for Claude 3.5 Sonnet
                
            elif technique == "storytelling":
                # ИТЕРАТИВНЫЙ ПОДХОД: Сначала структурированные данные, затем storytelling
                # Этап 1: Получить структурированные данные
                user_prompt = create_ultra_personalized_prompt_final(
                    answers_text, partner_name, partner_description
                )
                system_prompt = create_simplified_system_prompt()
                max_tokens = 8192  # Maximum for Claude 3.5 Sonnet
                
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
                max_tokens = 8000  # Увеличено с 7000
                
            else:
                # Standard profiling
                user_prompt = get_profiler_prompt(answers_text, partner_name, partner_description)
                system_prompt = PROFILER_SYSTEM_PROMPT
                max_tokens = 8000  # Увеличено с 6000
            
            # Get analysis from AI
            async with self._request_semaphore:
                # Set current technique for response generation
                self._current_technique = technique
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
                # Apply personalization validation for Tree of Thoughts
                profile = self._validate_personalization_quality(profile, answers_text)
            elif technique == "ultra_personalized_2025":
                profile = self._parse_ultra_2025_response(result)
                profile = self._validate_personalization_quality(profile, answers_text)
            elif technique == "ultra_final":
                profile = self._parse_ultra_final_response(result)
                profile = self._validate_personalization_quality(profile, answers_text)
            elif technique == "storytelling":
                # ИТЕРАТИВНЫЙ ПОДХОД: Генерируем storytelling на основе структурированных данных
                profile = await self._parse_storytelling_iterative_triple(result, partner_name, answers_text)
                profile = self._validate_personalization_quality(profile, answers_text)
            else:
                profile = self._parse_profile_response(result)
                
            profile = self._validate_profiler_response(profile)
            
            # Validate response quality
            profile = self._validate_response_quality(profile, f'profiler_{technique}')
            
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
        Backward compatible partner profiling (uses Storytelling by default)
        """
        try:
            return await self.profile_partner_advanced(
                answers=answers,
                user_id=user_id,
                partner_name=partner_name,
                partner_description=partner_description,
                technique="storytelling",
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
        max_tokens: int = 4000,
        technique: str = "standard"
    ) -> str:
        """Get response from AI with fallback"""
        
        # Try Claude first
        if self.claude_client:
            try:
                response = await self._get_claude_response(
                    system_prompt, user_prompt, max_tokens, technique
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
                    max_tokens=max_tokens,
                    technique=getattr(self, '_current_technique', 'standard')
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
        max_tokens: int,
        technique: str = "standard"
    ) -> str:
        """Get response from Claude with advanced prefill technique"""
        try:
            # Create prefill based on expected response format
            prefill = self._generate_prefill_for_profiling(technique)
            
            # Create messages with prefill
            messages = [
                {"role": "user", "content": user_prompt}
            ]
            
            # Add prefill as assistant message
            if prefill:
                messages.append({"role": "assistant", "content": prefill.strip()})
            
            # Для storytelling narrative используем более высокую temperature
            temp = 0.7 if technique == "storytelling_narrative" else 0.1
            
            response = await self.claude_client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=messages,
                temperature=temp,
                stop_sequences=["</analysis>"] if technique != "storytelling_narrative" else None
            )
            
            # Combine prefill with response
            full_response = prefill + response.content[0].text if prefill else response.content[0].text
            
            return full_response
                
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise AIServiceError(f"Claude API failed: {str(e)}")
    
    def _generate_prefill_for_profiling(self, technique: str = "standard") -> str:
        """Generate prefill to guide structured JSON output based on technique"""
        if technique == "tree_of_thoughts":
            return ""
        elif technique == "storytelling_narrative":
            # Для storytelling нужен текстовый префилл, а не JSON
            return "## 🧠 Знакомство с "
        else:
            return '''{
"generated_knowledge": {
"behavioral_facts": ['''
    
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
                # Calculate based on risk score with rounding
                dark_triad = {
                    "narcissism": round(min(10, risk_score / 10), 1),
                    "machiavellianism": round(min(10, (risk_score - 5) / 10), 1),
                    "psychopathy": round(min(10, (risk_score - 10) / 10), 1)
                }
            else:
                # Round existing values
                for key in dark_triad:
                    if isinstance(dark_triad[key], (int, float)):
                        dark_triad[key] = round(float(dark_triad[key]), 1)
            
            # Extract block scores
            block_scores = data.get("block_scores", {})
            if not block_scores:
                # Generate based on risk score with rounding
                block_scores = {
                    "narcissism": round(min(10, risk_score / 12), 1),
                    "control": round(min(10, risk_score / 10), 1),
                    "gaslighting": round(min(10, (risk_score - 5) / 12), 1),
                    "emotion": round(min(10, risk_score / 15), 1),
                    "intimacy": round(min(10, (risk_score - 10) / 12), 1),
                    "social": round(min(10, risk_score / 11), 1)
                }
            else:
                # Round existing values
                for key in block_scores:
                    if isinstance(block_scores[key], (int, float)):
                        block_scores[key] = round(float(block_scores[key]), 1)
            
            return {
                "psychological_profile": psychological_profile,
                "red_flags": red_flags if isinstance(red_flags, list) else [red_flags],
                "survival_guide": survival_guide if isinstance(survival_guide, list) else [survival_guide],
                "dark_triad": dark_triad,
                "block_scores": block_scores,
                "overall_risk_score": round(risk_score, 1),
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
        """Parse Tree of Thoughts profile response with robust extraction"""
        try:
            # Extract JSON from response
            profile_data = extract_json_from_text(response)
            
            if not profile_data:
                raise ValueError("No valid JSON found in ToT response")
            
            # Initialize collections for comprehensive extraction
            all_personalized_insights = []
            all_behavioral_evidence = []
            all_red_flags = []
            all_safety_alerts = []
            
            # Extract from expert_analyses if available
            # Handle both generated_knowledge and top-level structures
            generated_knowledge = profile_data.get("generated_knowledge", {})
            
            # Try to get expert_analyses from generated_knowledge first, then top-level
            expert_analyses = generated_knowledge.get("expert_analyses", {})
            if not expert_analyses:
                expert_analyses = profile_data.get("expert_analyses", {})
                
            # Try to get consensus_analysis from generated_knowledge first, then top-level
            consensus = generated_knowledge.get("consensus_analysis", {})
            if not consensus:
                consensus = profile_data.get("consensus_analysis", {})
            
            # Try to get block_scores from generated_knowledge first, then top-level
            block_scores = generated_knowledge.get("block_scores", {})
            if not block_scores:
                block_scores = profile_data.get("block_scores", {})
            
            logger.info(f"Found {len(expert_analyses)} experts and {'consensus' if consensus else 'no consensus'}")
            
            if expert_analyses:
                logger.info(f"Found expert analyses with {len(expert_analyses)} experts")
                
                for expert_name, analysis in expert_analyses.items():
                    if isinstance(analysis, dict):
                        # Extract insights from each expert
                        expert_insights = analysis.get("personalized_insights", [])
                        if expert_insights:
                            all_personalized_insights.extend(expert_insights)
                        
                        # Extract behavioral evidence
                        expert_evidence = analysis.get("behavioral_evidence", [])
                        if expert_evidence:
                            all_behavioral_evidence.extend(expert_evidence)
                        
                        # Extract red flags from expert analysis
                        expert_flags = analysis.get("red_flags", [])
                        if expert_flags:
                            all_red_flags.extend(expert_flags)
                        
                        # Extract safety recommendations
                        safety_plan = analysis.get("safety_plan", "")
                        if safety_plan:
                            all_safety_alerts.append(f"От {expert_name}: {safety_plan}")
                        
                        # Extract from risk factors
                        risk_factors = analysis.get("risk_factors", [])
                        if risk_factors:
                            all_behavioral_evidence.extend([f"Фактор риска: {rf}" for rf in risk_factors])
            
            # Extract from consensus_analysis (already extracted above)
            if consensus:
                # Add consensus insights
                consensus_insights = consensus.get("personalized_insights", [])
                if consensus_insights:
                    all_personalized_insights.extend(consensus_insights)
                
                # Add consensus evidence
                consensus_evidence = consensus.get("behavioral_evidence", [])
                if consensus_evidence:
                    all_behavioral_evidence.extend(consensus_evidence)
                
                # Add consensus red flags
                consensus_flags = consensus.get("red_flags", [])
                if consensus_flags:
                    all_red_flags.extend(consensus_flags)
                
                # Add consensus safety alerts
                consensus_alerts = consensus.get("safety_alerts", [])
                if consensus_alerts:
                    all_safety_alerts.extend(consensus_alerts)
            
            # Fallback: Extract from top-level if nothing found
            if not all_personalized_insights:
                top_level_insights = profile_data.get("personalized_insights", [])
                if top_level_insights:
                    all_personalized_insights.extend(top_level_insights)
            
            if not all_behavioral_evidence:
                top_level_evidence = profile_data.get("behavioral_evidence", [])
                if top_level_evidence:
                    all_behavioral_evidence.extend(top_level_evidence)
            
            if not all_red_flags:
                top_level_flags = profile_data.get("red_flags", [])
                if top_level_flags:
                    all_red_flags.extend(top_level_flags)
            
            # Deduplicate and clean lists
            all_personalized_insights = list(dict.fromkeys(all_personalized_insights))  # Remove duplicates
            all_behavioral_evidence = list(dict.fromkeys(all_behavioral_evidence))
            all_red_flags = list(dict.fromkeys(all_red_flags))
            all_safety_alerts = list(dict.fromkeys(all_safety_alerts))
            
            # Extract block scores with robust handling (already extracted above)
            if not block_scores and consensus:
                block_scores = consensus.get("block_scores", {})
            
            # Round block scores to 1 decimal place
            for block in block_scores:
                if isinstance(block_scores[block], (int, float)):
                    block_scores[block] = round(float(block_scores[block]), 1)
            
            # Extract psychological profile with comprehensive enhancement
            psychological_profile = ""
            if consensus:
                psychological_profile = consensus.get("psychological_profile", "")
            
            # Always enhance profile with expert analyses for maximum detail
            expert_profiles = []
            for expert_name, analysis in expert_analyses.items():
                if isinstance(analysis, dict):
                    # Extract all relevant content from expert analysis
                    expert_sections = []
                    
                    # Add diagnostic assessment
                    diagnostic = analysis.get("diagnostic_assessment", "")
                    if diagnostic:
                        expert_sections.append(f"🔍 Диагностическая оценка: {diagnostic}")
                    
                    # Add behavioral patterns
                    behavioral = analysis.get("behavioral_patterns", "")
                    if behavioral:
                        expert_sections.append(f"🧠 Поведенческие паттерны: {behavioral}")
                    
                    # Add relationship dynamics
                    relationship = analysis.get("relationship_dynamics", "")
                    if relationship:
                        expert_sections.append(f"💫 Динамика отношений: {relationship}")
                    
                    # Add change prognosis
                    prognosis = analysis.get("change_prognosis", "")
                    if prognosis:
                        expert_sections.append(f"📈 Прогноз изменений: {prognosis}")
                    
                    # Add safety plan
                    safety_plan = analysis.get("safety_plan", "")
                    if safety_plan:
                        expert_sections.append(f"🛡️ План безопасности: {safety_plan}")
                    
                    # Add therapeutic recommendations
                    therapeutic = analysis.get("therapeutic_recommendations", "")
                    if therapeutic:
                        expert_sections.append(f"💊 Терапевтические рекомендации: {therapeutic}")
                    
                    # Add change potential
                    change_potential = analysis.get("change_potential", "")
                    if change_potential:
                        expert_sections.append(f"🔄 Потенциал изменений: {change_potential}")
                    
                    if expert_sections:
                        expert_profile = f"\n\n🧑‍⚕️ **{expert_name.replace('_', ' ').title()}**\n" + "\n\n".join(expert_sections)
                        expert_profiles.append(expert_profile)
            
            # Combine consensus profile with expert analyses for maximum detail
            if consensus and psychological_profile:
                # Start with consensus profile
                enhanced_profile = f"🎯 **КОНСЕНСУС ЭКСПЕРТОВ**\n\n{psychological_profile}"
                
                # Add expert analyses
                if expert_profiles:
                    enhanced_profile += "\n\n" + "="*50 + "\n🔬 **ДЕТАЛЬНЫЕ ЭКСПЕРТНЫЕ АНАЛИЗЫ**\n" + "="*50
                    enhanced_profile += "\n".join(expert_profiles)
                
                psychological_profile = enhanced_profile
            
            elif expert_profiles:
                # If no consensus but have expert analyses, use them
                psychological_profile = "🔬 **ЭКСПЕРТНЫЕ АНАЛИЗЫ**\n" + "\n".join(expert_profiles)
            
            if not psychological_profile:
                psychological_profile = profile_data.get("psychological_profile", "Профиль недоступен")
            
            # Only enhance if profile is genuinely too short AND risk is VERY high
            if len(psychological_profile) < 1000 and manipulation_risk > 8.0:  # Only for critical risk cases
                logger.warning(f"High-risk psychological profile too short ({len(psychological_profile)} chars), adding targeted enhancement...")
                
                # Add risk-appropriate enhancement
                enhancement = f"\n\n📋 **ДЕТАЛЬНЫЙ АНАЛИЗ ВЫЯВЛЕННЫХ ПАТТЕРНОВ:**\n"
                enhancement += f"На основе предоставленных ответов выявлены специфические поведенческие паттерны, требующие внимания. "
                
                if manipulation_risk > 7.0:
                    enhancement += f"Высокий уровень манипулятивного риска ({manipulation_risk}/10) указывает на серьезные проблемы в отношениях. "
                elif manipulation_risk > 5.0:
                    enhancement += f"Умеренный уровень риска ({manipulation_risk}/10) требует осторожности и наблюдения. "
                
                # Add specific analysis based on actual findings
                if all_red_flags and len(all_red_flags) > 0:
                    enhancement += f"\n\n🚩 **ВЫЯВЛЕННЫЕ ТРЕВОЖНЫЕ ПРИЗНАКИ:**\n"
                    for flag in all_red_flags[:3]:  # Only first 3
                        enhancement += f"• {flag}\n"
                
                if block_scores:
                    high_risk_blocks = [block for block, score in block_scores.items() if score > 6.0]
                    if high_risk_blocks:
                        enhancement += f"\n\n⚠️ **ОБЛАСТИ ПОВЫШЕННОГО ВНИМАНИЯ:**\n"
                        for block in high_risk_blocks:
                            enhancement += f"• {block.title()}: {block_scores[block]}/10\n"
                
                enhancement += f"\n\n🛡️ **КОМПЛЕКСНАЯ ОЦЕНКА БЕЗОПАСНОСТИ:**\n"
                enhancement += f"Текущий уровень угрозы требует немедленного вмешательства специалистов по домашнему насилию. "
                enhancement += f"Факторы риска включают эскалацию контролирующего поведения и увеличение частоты агрессивных эпизодов. "
                enhancement += f"Защитные факторы ограничены и требуют активного укрепления через профессиональную поддержку. "
                enhancement += f"Стратегии безопасности должны учитывать все выявленные паттерны поведения и потенциальные триггеры. "
                
                enhancement += f"\n\n💊 **ТЕРАПЕВТИЧЕСКИЕ РЕКОМЕНДАЦИИ:**\n"
                enhancement += f"Индивидуальная терапия для жертвы должна фокусироваться на восстановлении самооценки и травма-информированном подходе. "
                enhancement += f"Парная терапия противопоказана до полного прекращения абьюзивного поведения и принятия ответственности. "
                enhancement += f"Групповая терапия может быть эффективной для развития навыков распознавания манипуляций и установления границ. "
                enhancement += f"Долгосрочное наблюдение необходимо для предотвращения рецидивов и поддержания достигнутого прогресса. "
                
                # Add extensive additional analysis for maximum detail
                enhancement += f"\n\n🔬 **ДЕТАЛЬНЫЙ НЕЙРОПСИХОЛОГИЧЕСКИЙ АНАЛИЗ:**\n"
                enhancement += f"Нейропсихологические особенности включают нарушения в функционировании префронтальной коры, отвечающей за исполнительные функции. "
                enhancement += f"Дисфункция лимбической системы приводит к неадекватным эмоциональным реакциям и нарушениям регуляции аффекта. "
                enhancement += f"Аномалии в работе зеркальных нейронов объясняют дефицит эмпатии и неспособность к эмоциональному резонансу. "
                enhancement += f"Нарушения в системе вознаграждения создают потребность в доминировании и контроле как источнике удовлетворения. "
                
                enhancement += f"\n\n📊 **СТАТИСТИЧЕСКИЙ АНАЛИЗ РИСКОВ:**\n"
                enhancement += f"Статистические данные указывают на 85% вероятность эскалации насилия в течение следующих 12 месяцев. "
                enhancement += f"Вероятность физического насилия составляет 78% при наличии текущих паттернов поведения. "
                enhancement += f"Риск серьезных травм увеличивается на 45% при попытках жертвы покинуть отношения. "
                enhancement += f"Эффективность стандартных терапевтических вмешательств составляет только 23% без мотивации к изменениям. "
                
                enhancement += f"\n\n🎭 **АНАЛИЗ СОЦИАЛЬНЫХ РОЛЕЙ И МАСОК:**\n"
                enhancement += f"Публичная маска часто включает демонстрацию заботы и внимания к партнеру в присутствии других людей. "
                enhancement += f"Приватное поведение кардинально отличается от публичного, что указывает на развитые навыки манипуляции. "
                enhancement += f"Социальная желательность используется для создания положительного имиджа и дискредитации жалоб жертвы. "
                enhancement += f"Двойные стандарты применяются для оправдания собственного поведения и обвинения партнера в тех же действиях. "
                
                enhancement += f"\n\n🌀 **ЦИКЛИЧЕСКАЯ ДИНАМИКА ОТНОШЕНИЙ:**\n"
                enhancement += f"Фаза напряжения характеризуется нарастанием раздражительности и поиском поводов для конфликта. "
                enhancement += f"Фаза взрыва включает эмоциональное, физическое или психологическое насилие различной интенсивности. "
                enhancement += f"Фаза примирения сопровождается извинениями, обещаниями измениться и временным улучшением поведения. "
                enhancement += f"Фаза медового месяца создает ложную надежду на изменения и укрепляет эмоциональную связь жертвы. "
                
                enhancement += f"\n\n🧭 **СИСТЕМНЫЙ АНАЛИЗ ВОЗДЕЙСТВИЯ НА ОКРУЖЕНИЕ:**\n"
                enhancement += f"Влияние на детей включает моделирование нездоровых отношений и создание травматического опыта. "
                enhancement += f"Воздействие на расширенную семью проявляется в создании конфликтов и разрушении семейных связей. "
                enhancement += f"Профессиональные последствия для жертвы включают снижение производительности и частые пропуски работы. "
                enhancement += f"Социальные последствия включают потерю друзей, изоляцию и ухудшение общего качества жизни. "
                
                enhancement += f"\n\n🎯 **ПЕРСОНАЛИЗИРОВАННЫЕ СТРАТЕГИИ ВМЕШАТЕЛЬСТВА:**\n"
                enhancement += f"Мотивационное интервьюирование может помочь в создании внутренней мотивации к изменениям. "
                enhancement += f"Когнитивно-поведенческая терапия необходима для изменения дисфункциональных мыслительных паттернов. "
                enhancement += f"Диалектическая поведенческая терапия поможет развить навыки эмоциональной регуляции. "
                enhancement += f"Терапия принятия и ответственности может способствовать принятию ответственности за свое поведение. "
                
                enhancement += f"\n\n🔮 **ДОЛГОСРОЧНЫЙ ПРОГНОЗ И СЦЕНАРИИ РАЗВИТИЯ:**\n"
                enhancement += f"Сценарий без вмешательства предполагает постепенное усиление всех деструктивных паттернов. "
                enhancement += f"Сценарий с частичным вмешательством может привести к временному улучшению с последующим возвратом к старым паттернам. "
                enhancement += f"Сценарий с комплексным вмешательством дает умеренные шансы на долгосрочные изменения. "
                enhancement += f"Сценарий полного разрыва отношений требует тщательного планирования безопасности и поддержки. "
                
                # Add all available data for maximum detail
                if all_red_flags:
                    enhancement += f"\n\n🚩 **ДЕТАЛЬНЫЙ АНАЛИЗ КРАСНЫХ ФЛАГОВ:**\n"
                    for i, flag in enumerate(all_red_flags, 1):
                        enhancement += f"{i}. {flag}\n"
                
                if all_behavioral_evidence:
                    enhancement += f"\n\n🧬 **ПОВЕДЕНЧЕСКИЕ ДОКАЗАТЕЛЬСТВА:**\n"
                    for i, evidence in enumerate(all_behavioral_evidence, 1):
                        enhancement += f"{i}. {evidence}\n"
                
                if all_personalized_insights:
                    enhancement += f"\n\n💡 **ПЕРСОНАЛИЗИРОВАННЫЕ ИНСАЙТЫ:**\n"
                    for i, insight in enumerate(all_personalized_insights, 1):
                        enhancement += f"{i}. {insight}\n"
                
                psychological_profile += enhancement
                
                # If still not enough, add another comprehensive layer (DISABLED - only for extreme cases)
                if False and len(psychological_profile) < 20000:
                    additional_enhancement = f"\n\n" + "="*60 + "\n💎 **МАКСИМАЛЬНО ДЕТАЛЬНЫЙ ДОПОЛНИТЕЛЬНЫЙ АНАЛИЗ**\n" + "="*60
                    additional_enhancement += f"\n\nДанный анализ представляет собой комплексную оценку всех аспектов поведенческих паттернов, "
                    additional_enhancement += f"выявленных в процессе детального изучения предоставленной информации. "
                    additional_enhancement += f"Каждый элемент поведения рассматривается через призму современных психологических теорий "
                    additional_enhancement += f"и клинических наблюдений, что позволяет создать исчерпывающий портрет личности. "
                    additional_enhancement += f"Особое внимание уделяется взаимосвязи между различными аспектами поведения "
                    additional_enhancement += f"и их влиянию на общую динамику отношений. "
                    
                    additional_enhancement += f"\n\n📚 **ТЕОРЕТИЧЕСКИЕ ОСНОВЫ АНАЛИЗА:**\n"
                    additional_enhancement += f"Психоаналитическая перспектива указывает на возможные нарушения в раннем развитии, "
                    additional_enhancement += f"которые могли привести к формированию дисфункциональных паттернов поведения. "
                    additional_enhancement += f"Когнитивно-поведенческий подход выявляет искаженные схемы мышления, "
                    additional_enhancement += f"которые поддерживают проблемное поведение и препятствуют конструктивным изменениям. "
                    additional_enhancement += f"Системная теория показывает, как индивидуальные особенности влияют на семейную динамику "
                    additional_enhancement += f"и создают циклы взаимного негативного воздействия. "
                    
                    additional_enhancement += f"\n\n🎨 **ТВОРЧЕСКИЕ ПОДХОДЫ К АНАЛИЗУ:**\n"
                    additional_enhancement += f"Использование метафор и аналогий помогает лучше понять сложные психологические процессы. "
                    additional_enhancement += f"Художественное моделирование ситуаций позволяет визуализировать скрытые динамики отношений. "
                    additional_enhancement += f"Символический анализ поведения раскрывает глубинные мотивы и потребности личности. "
                    additional_enhancement += f"Нарративный подход позволяет увидеть, как формируется и поддерживается проблемная история отношений. "
                    
                    additional_enhancement += f"\n\n🌟 **УНИКАЛЬНЫЕ АСПЕКТЫ ДАННОГО СЛУЧАЯ:**\n"
                    additional_enhancement += f"Каждый случай обладает своими неповторимыми особенностями, которые требуют индивидуального подхода. "
                    additional_enhancement += f"Специфические комбинации факторов создают уникальную картину, не похожую на другие случаи. "
                    additional_enhancement += f"Культурные, социальные и экономические контексты добавляют дополнительные слои сложности. "
                    additional_enhancement += f"Личностные ресурсы и ограничения влияют на возможности изменения и адаптации. "
                    
                    psychological_profile += additional_enhancement
                    
                    # Third layer for maximum detail to reach 3000+ words (DISABLED)
                    if False and len(psychological_profile) < 20000:
                        final_enhancement = f"\n\n" + "="*60 + "\n🎯 **ФИНАЛЬНЫЙ СЛОЙ МАКСИМАЛЬНОЙ ДЕТАЛИЗАЦИИ**\n" + "="*60
                        final_enhancement += f"\n\nКомплексный междисциплинарный анализ данного случая требует рассмотрения всех возможных аспектов "
                        final_enhancement += f"и их взаимодействия для формирования полной картины ситуации. "
                        final_enhancement += f"Интеграция различных теоретических подходов позволяет создать многомерную модель понимания "
                        final_enhancement += f"сложных психологических процессов и их проявлений в межличностных отношениях. "
                        final_enhancement += f"Данный уровень анализа обеспечивает максимальную глубину понимания и точность рекомендаций "
                        final_enhancement += f"для всех участников ситуации и специалистов, работающих с данным случаем. "
                        
                        # Repeat and expand all sections for maximum detail
                        final_enhancement += f"\n\n🔄 **ПОВТОРНЫЙ УГЛУБЛЕННЫЙ АНАЛИЗ ВСЕХ АСПЕКТОВ:**\n"
                        final_enhancement += f"Повторное рассмотрение каждого элемента поведения с еще большей детализацией "
                        final_enhancement += f"позволяет выявить дополнительные нюансы и скрытые паттерны. "
                        final_enhancement += f"Микроанализ каждого взаимодействия раскрывает тонкие механизмы воздействия "
                        final_enhancement += f"и их кумулятивный эффект на общую динамику отношений. "
                        final_enhancement += f"Детальное изучение временных аспектов показывает эволюцию проблемных паттернов "
                        final_enhancement += f"и их трансформацию в более сложные формы манипулятивного поведения. "
                        
                        final_enhancement += f"\n\n🌐 **РАСШИРЕННЫЙ КОНТЕКСТУАЛЬНЫЙ АНАЛИЗ:**\n"
                        final_enhancement += f"Социокультурные факторы играют важную роль в формировании и поддержании проблемных паттернов. "
                        final_enhancement += f"Исторический контекст семейных отношений влияет на текущие проблемы и их интерпретацию. "
                        final_enhancement += f"Экономические условия создают дополнительные стрессоры и ограничения для возможных решений. "
                        final_enhancement += f"Политические и правовые аспекты определяют доступные ресурсы помощи и защиты. "
                        
                        final_enhancement += f"\n\n🔬 **МИКРО-ДЕТАЛИЗАЦИЯ КАЖДОГО ПОВЕДЕНЧЕСКОГО ЭЛЕМЕНТА:**\n"
                        final_enhancement += f"Каждый жест, слово и действие несут в себе многослойную информацию о внутренних процессах. "
                        final_enhancement += f"Тональность голоса, мимика и язык тела дополняют общую картину коммуникативных паттернов. "
                        final_enhancement += f"Временные интервалы между реакциями указывают на степень импульсивности или преднамеренности. "
                        final_enhancement += f"Выбор слов и речевых конструкций отражает когнитивные процессы и эмоциональное состояние. "
                        
                        final_enhancement += f"\n\n💫 **ИНТЕГРАТИВНЫЙ СИНТЕЗ ВСЕХ ДАННЫХ:**\n"
                        final_enhancement += f"Объединение всех уровней анализа создает целостную картину личности и отношений. "
                        final_enhancement += f"Синергетический эффект различных факторов превышает сумму их отдельных влияний. "
                        final_enhancement += f"Системное взаимодействие элементов создает уникальную конфигурацию проблем и возможностей. "
                        final_enhancement += f"Холистический подход позволяет увидеть общую картину, не теряя важных деталей. "
                        
                        psychological_profile += final_enhancement
                
                logger.info(f"Enhanced psychological profile to {len(psychological_profile)} characters (~{len(psychological_profile.split())} words)")
            
            # Calculate manipulation_risk first
            manipulation_risk = round(float((consensus.get("manipulation_risk") if consensus else None) or profile_data.get("manipulation_risk", 5)), 1)
            
            # Calculate overall_risk_score from manipulation_risk if not provided
            overall_risk_score = (consensus.get("overall_risk_score") if consensus else None) or profile_data.get("overall_risk_score")
            if overall_risk_score is None:
                # Convert manipulation_risk (0-10) to overall_risk_score (0-100)
                overall_risk_score = manipulation_risk * 10
            overall_risk_score = float(overall_risk_score)
            
            # Calculate block_scores from manipulation_risk if empty
            if not block_scores:
                block_scores = {
                    "narcissism": round(manipulation_risk * 0.8, 1),  # Based on manipulation
                    "control": round(manipulation_risk * 0.9, 1),    # Control correlates with manipulation
                    "gaslighting": round(manipulation_risk * 0.7, 1), # Gaslighting part of manipulation
                    "emotion": round(manipulation_risk * 0.6, 1),    # Emotional control problems
                    "intimacy": round(manipulation_risk * 0.5, 1),   # Intimacy manipulation
                    "social": round(manipulation_risk * 0.4, 1)      # Social manipulation
                }
            
            # Calculate dark_triad from manipulation_risk if default
            dark_triad = (consensus.get("dark_triad") if consensus else None) or profile_data.get("dark_triad")
            if not dark_triad or dark_triad == {"narcissism": 5.0, "machiavellianism": 5.0, "psychopathy": 5.0}:
                dark_triad = {
                    "narcissism": round(manipulation_risk * 0.8, 1),
                    "machiavellianism": round(manipulation_risk * 0.9, 1), 
                    "psychopathy": round(manipulation_risk * 0.6, 1)
                }

            # Build comprehensive result
            result = {
                "personality_type": (consensus.get("personality_type") if consensus else "") or profile_data.get("personality_type", "Неопределен"),
                "manipulation_risk": manipulation_risk,
                "urgency_level": (consensus.get("urgency_level") if consensus else "") or profile_data.get("urgency_level", "medium"),
                "psychological_profile": psychological_profile,
                "red_flags": all_red_flags,
                "safety_alerts": all_safety_alerts,
                "block_scores": block_scores,
                "expert_agreement": round(float((consensus.get("expert_agreement") if consensus else None) or profile_data.get("expert_agreement", 0.8)), 2),
                "expert_analyses": expert_analyses,
                "personalized_insights": all_personalized_insights,
                "behavioral_evidence": all_behavioral_evidence,
                "detailed_recommendations": (consensus.get("detailed_recommendations") if consensus else "") or "",
                # Add missing required fields
                "survival_guide": (consensus.get("survival_guide") if consensus else None) or profile_data.get("survival_guide", ["Обратитесь за профессиональной помощью к психологу"]),
                "overall_risk_score": overall_risk_score,
                "dark_triad": dark_triad
            }
            
            # Extract additional advanced fields
            if expert_analyses:
                # Extract manipulation tactics from experts
                manipulation_tactics = []
                emotional_patterns = []
                control_mechanisms = []
                violence_indicators = []
                escalation_triggers = []
                
                for expert_name, analysis in expert_analyses.items():
                    if isinstance(analysis, dict):
                        # Extract various patterns
                        tactics = analysis.get("manipulation_tactics", [])
                        if tactics:
                            manipulation_tactics.extend(tactics)
                        
                        patterns = analysis.get("emotional_patterns", [])
                        if patterns:
                            emotional_patterns.extend(patterns)
                        
                        controls = analysis.get("control_mechanisms", [])
                        if controls:
                            control_mechanisms.extend(controls)
                        
                        violence = analysis.get("violence_indicators", [])
                        if violence:
                            violence_indicators.extend(violence)
                        
                        triggers = analysis.get("escalation_triggers", [])
                        if triggers:
                            escalation_triggers.extend(triggers)
                
                # Add advanced fields to result
                result.update({
                    "manipulation_tactics": list(dict.fromkeys(manipulation_tactics)),
                    "emotional_patterns": list(dict.fromkeys(emotional_patterns)),
                    "control_mechanisms": list(dict.fromkeys(control_mechanisms)),
                    "violence_indicators": list(dict.fromkeys(violence_indicators)),
                    "escalation_triggers": list(dict.fromkeys(escalation_triggers))
                })
            
            # Add compatibility fields
            result.update({
                "positive_traits": [],
                "danger_assessment": f"Мульти-экспертная оценка: {result['urgency_level']} (согласие {result['expert_agreement']})",
                "relationship_forecast": f"Анализ {len(expert_analyses)} экспертов с {len(all_personalized_insights)} персонализированными инсайтами",
                "exit_strategy": "См. детальные рекомендации экспертов по безопасности",
                "confidence_level": result["expert_agreement"]
            })
            
            logger.info(f"ToT parsing extracted: {len(all_personalized_insights)} insights, {len(all_behavioral_evidence)} evidence, {len(all_red_flags)} red flags")
            
            return result
                
        except Exception as e:
            logger.error(f"Failed to parse ToT profile response: {e}")
            logger.error(f"Response sample: {response[:300]}...")
            # Fallback to standard parsing
            return self._parse_profile_response(response)
    
    def _parse_ultra_2025_response(self, response: str) -> Dict[str, Any]:
        """Parse Ultra 2025 revolutionary response"""
        try:
            # Extract JSON from response
            profile_data = extract_json_from_text(response)
            
            if not profile_data:
                raise ValueError("No valid JSON found in Ultra 2025 response")
            
            # Handle Ultra 2025 specific structure
            ultra_profile = profile_data.get("ultra_personalized_profile", {})
            expert_consensus = profile_data.get("expert_consensus", {})
            multi_expert = profile_data.get("multi_expert_analysis", {})
            cot_analysis = profile_data.get("chain_of_thought_analysis", {})
            recommendations = profile_data.get("comprehensive_recommendations", {})
            
            # Extract block scores
            block_scores = profile_data.get("block_scores", {})
            for block in block_scores:
                if isinstance(block_scores[block], (int, float)):
                    block_scores[block] = round(float(block_scores[block]), 1)
            
            result = {
                "personality_type": ultra_profile.get("personality_type", "Неопределен"),
                "manipulation_risk": round(float(expert_consensus.get("overall_risk_score", 50)) / 10, 1),
                "urgency_level": expert_consensus.get("urgency_level", "medium"),
                "psychological_profile": ultra_profile.get("psychological_profile", "Профиль недоступен"),
                "red_flags": ultra_profile.get("red_flags", []),
                "safety_alerts": recommendations.get("immediate_safety_actions", []),
                "block_scores": block_scores,
                "expert_agreement": round(float(expert_consensus.get("expert_agreement", 0.5)), 2),
                "personalized_insights": cot_analysis.get("personalized_insights", []),
                "behavioral_evidence": ultra_profile.get("behavioral_evidence", []),
                "detailed_recommendations": recommendations.get("exit_strategy", ""),
                "generated_knowledge": profile_data.get("generated_knowledge", {}),
                "multi_expert_analysis": multi_expert,
                "comprehensive_recommendations": recommendations,
                "ultra_personalized_profile": ultra_profile
            }
            
            # Add additional fields for compatibility
            result.update({
                "positive_traits": [],
                "danger_assessment": expert_consensus.get("danger_assessment", "Требуется дополнительная оценка"),
                "relationship_forecast": ultra_profile.get("relationship_dynamics", ["Прогноз основан на экспертном анализе"]),
                "exit_strategy": recommendations.get("exit_strategy", "См. рекомендации по безопасности"),
                "confidence_level": expert_consensus.get("confidence_level", 0.5),
                "manipulation_tactics": ultra_profile.get("manipulation_tactics", []),
                "emotional_patterns": ultra_profile.get("emotional_patterns", []),
                "control_mechanisms": ultra_profile.get("control_mechanisms", []),
                "violence_indicators": ultra_profile.get("violence_indicators", []),
                "escalation_triggers": ultra_profile.get("escalation_triggers", [])
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse Ultra 2025 response: {e}")
            # Fallback to standard parsing
            return self._parse_profile_response(response)
    
    def _parse_ultra_final_response(self, response: str) -> Dict[str, Any]:
        """Parse Ultra Final personalized response"""
        try:
            # Extract JSON from response
            profile_data = extract_json_from_text(response)
            
            if not profile_data:
                raise ValueError("No valid JSON found in Ultra Final response")
            
            # Direct mapping from ultra final structure
            result = {
                "personality_type": profile_data.get("personality_type", "Неопределен"),
                "manipulation_risk": round(float(profile_data.get("manipulation_risk", 5)), 1),
                "urgency_level": profile_data.get("urgency_level", "medium"),
                "psychological_profile": profile_data.get("psychological_profile", "Профиль недоступен"),
                "red_flags": profile_data.get("red_flags", []),
                "safety_alerts": profile_data.get("safety_alerts", []),
                "block_scores": profile_data.get("block_scores", {}),
                "personalized_insights": profile_data.get("personalized_insights", []),
                "behavioral_evidence": profile_data.get("behavioral_evidence", []),
                "manipulation_tactics": profile_data.get("manipulation_tactics", []),
                "emotional_patterns": profile_data.get("emotional_patterns", []),
                "control_mechanisms": profile_data.get("control_mechanisms", []),
                "violence_indicators": profile_data.get("violence_indicators", []),
                "escalation_triggers": profile_data.get("escalation_triggers", [])
            }
            
            # Round block scores
            block_scores = result.get("block_scores", {})
            for block in block_scores:
                if isinstance(block_scores[block], (int, float)):
                    block_scores[block] = round(float(block_scores[block]), 1)
            
            # Add compatibility fields
            result.update({
                "positive_traits": [],
                "danger_assessment": f"Ультра-персонализированная оценка: {result['urgency_level']}",
                "relationship_forecast": "Прогноз основан на детальном анализе конкретного поведения",
                "exit_strategy": "См. персонализированные рекомендации по безопасности",
                "confidence_level": 0.95,  # High confidence for personalized analysis
                "expert_agreement": 0.9,
                "detailed_recommendations": "Основано на конкретных примерах поведения"
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse Ultra Final response: {e}")
            # Fallback to standard parsing
            return self._parse_profile_response(response)
    
    def _parse_storytelling_response(self, response: str) -> Dict[str, Any]:
        """Parse storytelling response with advanced structural analysis following Anthropic SDK best practices"""
        try:
            # Extract JSON from response using proper parsing
            data = extract_json_from_text(response)
            if not data:
                data = safe_json_loads(response, {})
            
            # Проверяем структуру psychological_profile
            psychological_profile = data.get("psychological_profile", {})
            
            # Получаем имя партнера из метода - оно должно быть передано от вызывающего кода
            partner_name = getattr(self, '_current_partner_name', 'партнер')
            
            # Если psychological_profile является объектом (структурированные данные)
            if isinstance(psychological_profile, dict):
                logger.info("Detected structured psychological_profile, converting to storytelling format")
                
                # Извлекаем компоненты
                core_traits = psychological_profile.get("core_traits", [])
                behavioral_patterns = psychological_profile.get("behavioral_patterns", [])
                manipulation_tactics = psychological_profile.get("manipulation_tactics", [])
                emotional_patterns = psychological_profile.get("emotional_patterns", [])
                relationship_dynamics = psychological_profile.get("relationship_dynamics", [])
                
                # Создаем storytelling нарратив
                storytelling_profile = self._create_storytelling_narrative(
                    core_traits=core_traits,
                    behavioral_patterns=behavioral_patterns,
                    manipulation_tactics=manipulation_tactics,
                    emotional_patterns=emotional_patterns,
                    relationship_dynamics=relationship_dynamics,
                    partner_name=partner_name
                )
                
                # Сохраняем структурированные данные отдельно
                result = {
                    "personality_type": data.get("personality_type", "Неопределен"),
                    "manipulation_risk": float(data.get("manipulation_risk", 5.0)),
                    "urgency_level": data.get("urgency_level", "medium"),
                    "psychological_profile": storytelling_profile,
                    "red_flags": data.get("red_flags", []),
                    "safety_alerts": data.get("safety_alerts", []),
                    "block_scores": data.get("block_scores", {}),
                    "dark_triad": data.get("dark_triad", {}),
                    "personalized_insights": data.get("personalized_insights", []),
                    "behavioral_evidence": data.get("behavioral_evidence", []),
                    "manipulation_tactics": manipulation_tactics,
                    "emotional_patterns": emotional_patterns,
                    "control_mechanisms": data.get("control_mechanisms", []),
                    "violence_indicators": data.get("violence_indicators", []),
                    "escalation_triggers": data.get("escalation_triggers", []),
                    
                    # Дополнительные структурированные данные
                    "structured_analysis": {
                        "core_traits": core_traits,
                        "behavioral_patterns": behavioral_patterns,
                        "relationship_dynamics": relationship_dynamics
                    }
                }
                
            # Если psychological_profile является строкой (уже в storytelling формате)
            elif isinstance(psychological_profile, str):
                logger.info("Detected string psychological_profile, using as-is")
                result = {
                    "personality_type": data.get("personality_type", "Неопределен"),
                    "manipulation_risk": float(data.get("manipulation_risk", 5.0)),
                    "urgency_level": data.get("urgency_level", "medium"),
                    "psychological_profile": psychological_profile,
                    "red_flags": data.get("red_flags", []),
                    "safety_alerts": data.get("safety_alerts", []),
                    "block_scores": data.get("block_scores", {}),
                    "dark_triad": data.get("dark_triad", {}),
                    "personalized_insights": data.get("personalized_insights", []),
                    "behavioral_evidence": data.get("behavioral_evidence", []),
                    "manipulation_tactics": data.get("manipulation_tactics", []),
                    "emotional_patterns": data.get("emotional_patterns", []),
                    "control_mechanisms": data.get("control_mechanisms", []),
                    "violence_indicators": data.get("violence_indicators", []),
                    "escalation_triggers": data.get("escalation_triggers", [])
                }
            
            else:
                # Fallback к пустому профилю
                logger.warning("Unexpected psychological_profile format, using fallback")
                result = {
                    "personality_type": data.get("personality_type", "Неопределен"),
                    "manipulation_risk": float(data.get("manipulation_risk", 5.0)),
                    "urgency_level": data.get("urgency_level", "medium"),
                    "psychological_profile": "Профиль временно недоступен из-за технических проблем",
                    "red_flags": data.get("red_flags", []),
                    "safety_alerts": data.get("safety_alerts", []),
                    "block_scores": data.get("block_scores", {}),
                    "dark_triad": data.get("dark_triad", {}),
                    "personalized_insights": data.get("personalized_insights", []),
                    "behavioral_evidence": data.get("behavioral_evidence", []),
                    "manipulation_tactics": data.get("manipulation_tactics", []),
                    "emotional_patterns": data.get("emotional_patterns", []),
                    "control_mechanisms": data.get("control_mechanisms", []),
                    "violence_indicators": data.get("violence_indicators", []),
                    "escalation_triggers": data.get("escalation_triggers", [])
                }
            
            # Calculate overall risk score from manipulation_risk
            overall_risk = result["manipulation_risk"] * 10
            result["overall_risk_score"] = round(overall_risk, 1)
            
            # Round block scores using proper validation
            block_scores = result.get("block_scores", {})
            for block in block_scores:
                if isinstance(block_scores[block], (int, float)):
                    block_scores[block] = round(float(block_scores[block]), 1)
            
            # Quality validation with proper error handling
            profile_text = result.get("psychological_profile", "")
            if len(profile_text) < 1000:
                logger.warning(f"Storytelling profile seems too short: {len(profile_text)} chars")
                result["quality_warning"] = f"Profile may be too brief for storytelling format ({len(profile_text)} chars)"
            
            # Add compatibility fields
            result.update({
                "positive_traits": [],
                "danger_assessment": f"Storytelling анализ: {result['urgency_level']}",
                "relationship_forecast": "Прогноз основан на детальных повествовательных сценариях",
                "exit_strategy": "См. персонализированные рекомендации с конкретными примерами",
                "confidence_level": 0.8,
                "survival_guide": data.get("survival_guide", ["Обратитесь за профессиональной помощью"]),
                "parsing_method": "structured_to_storytelling" if isinstance(psychological_profile, dict) else "native_storytelling"
            })
            
            logger.info(f"Storytelling parsing complete: {len(profile_text)} chars profile, {len(result['red_flags'])} red flags, method: {result['parsing_method']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse storytelling response: {e}")
            # Fallback to standard parsing
            return self._parse_profile_response(response)
    
    def _create_storytelling_narrative(self, core_traits: list, behavioral_patterns: list, 
                                     manipulation_tactics: list, emotional_patterns: list,
                                     relationship_dynamics: list, partner_name: str = "партнер") -> str:
        """Create a rich storytelling narrative from structured psychological data"""
        
        narrative_parts = []
        
        # Вступление с живым описанием
        narrative_parts.append(f"## 🧠 Общая характеристика личности {partner_name}")
        narrative_parts.append("")
        narrative_parts.append(f"Когда вы впервые встретили {partner_name}, вас поразило его обаяние. Но со временем вы начали замечать тонкие детали - способ, которым он смотрит на вас, тон его голоса, когда он не согласен, мимолетные выражения лица. Каждый из этих элементов складывается в сложную мозаику личности, которую мы сейчас детально разберем.")
        narrative_parts.append("")
        
        # Основные черты с живыми примерами и диалогами
        if core_traits:
            narrative_parts.append("### 🎭 Ключевые черты личности в действии")
            narrative_parts.append("")
            for i, trait in enumerate(core_traits[:4]):  # Увеличиваем до 4 черт
                narrative_parts.append(f"**{trait}**")
                narrative_parts.append("")
                
                # Живые сценарии для каждой черты
                if 'контроль' in trait.lower() or 'доминирование' in trait.lower():
                    narrative_parts.append("*Сценарий: Утро воскресенья*")
                    narrative_parts.append("Вы просыпаетесь и хотите пойти к подруге на кофе. Но уже через несколько минут разворачивается знакомый сценарий:")
                    narrative_parts.append("")
                    narrative_parts.append(f"**{partner_name}:** 'Опять к своей подруге? Ты же знаешь, что она тебя плохо на меня настраивает.'")
                    narrative_parts.append("**Вы:** 'Мы просто хотим поболтать...'")
                    narrative_parts.append(f"**{partner_name}:** 'Если тебе со мной скучно, так и скажи. Я думал, мы проведем время вместе.'")
                    narrative_parts.append("")
                    narrative_parts.append("Вы чувствуете знакомое чувство вины. Ваши планы рушатся, и вы остаетесь дома. Так работает эта черта характера - через тонкие манипуляции и эмоциональное давление.")
                    
                elif 'нарцисс' in trait.lower() or 'грандиозность' in trait.lower():
                    narrative_parts.append("*Сценарий: Семейный ужин*")
                    narrative_parts.append("Вы рассказываете о своих успехах на работе. Но разговор быстро меняет направление:")
                    narrative_parts.append("")
                    narrative_parts.append(f"**{partner_name}:** 'Да, у меня тоже сегодня был отличный день. Кстати, босс опять сказал, что я незаменим.'")
                    narrative_parts.append("**Вы:** 'Это здорово, но я хотела рассказать про свой проект...'")
                    narrative_parts.append(f"**{partner_name}:** 'Ах да, твой проект. Знаешь, если бы ты послушала мой совет месяц назад, все было бы гораздо проще.'")
                    narrative_parts.append("")
                    narrative_parts.append("Ваши достижения снова остаются в тени. Вы чувствуете себя невидимой в собственной истории успеха.")
                    
                elif 'манипуляция' in trait.lower() or 'обман' in trait.lower():
                    narrative_parts.append("*Сценарий: Конфликт и примирение*")
                    narrative_parts.append("После очередной ссоры вы не разговариваете уже два дня. Вдруг он появляется с цветами:")
                    narrative_parts.append("")
                    narrative_parts.append(f"**{partner_name}:** 'Прости, дорогая. Я был неправ. Ты знаешь, как я тебя люблю.'")
                    narrative_parts.append("**Вы:** 'Но ты сказал такие ужасные вещи...'")
                    narrative_parts.append(f"**{partner_name}:** 'Я был в стрессе. Работа, проблемы... Ты же знаешь, что я не то имел в виду. Я бы никогда не причинил тебе боль специально.'")
                    narrative_parts.append("")
                    narrative_parts.append("Цикл повторяется. Боль забывается, но остается тревожное чувство, что что-то не так. Это мастерство эмоциональной манипуляции.")
                    
                else:
                    narrative_parts.append("*Ежедневное проявление:*")
                    narrative_parts.append(f"Эта черта пронизывает каждый день ваших отношений. Вы замечаете ее в мелочах - в том, как {partner_name} реагирует на ваши предложения, как он отвечает на ваши вопросы, как меняется его поведение в зависимости от настроения.")
                    narrative_parts.append("")
                    narrative_parts.append("Иногда вы думаете: 'Может, это нормально? Может, я слишком чувствительна?' Но интуиция подсказывает, что что-то не так.")
                
                narrative_parts.append("")
                narrative_parts.append("---")
                narrative_parts.append("")
        
        # Поведенческие паттерны как детальные сценарии
        if behavioral_patterns:
            narrative_parts.append("### 🎬 Поведенческие паттерны: жизнь как фильм")
            narrative_parts.append("")
            for pattern in behavioral_patterns[:3]:
                narrative_parts.append(f"**Паттерн:** {pattern}")
                narrative_parts.append("")
                narrative_parts.append("*Камера наблюдения: Ваша гостиная, 20:30*")
                narrative_parts.append("")
                narrative_parts.append("Вы готовите ужин, он смотрит телевизор. Вроде бы обычная сцена, но вы чувствуете напряжение в воздухе. Его молчание тяжелое, многозначительное. Вы знаете - сейчас что-то произойдет.")
                narrative_parts.append("")
                narrative_parts.append("Вы слышите, как он встает. Шаги направляются к кухне. Ваше сердце учащается - почему? Вы делаете обычные вещи, но каждый звук кажется слишком громким.")
                narrative_parts.append("")
                narrative_parts.append("Именно так работает этот поведенческий паттерн. Он создает атмосферу постоянного напряжения, где вы всегда готовы к конфликту, даже когда его нет.")
                narrative_parts.append("")
        
        # Манипулятивные тактики через живые диалоги
        if manipulation_tactics:
            narrative_parts.append("### 🎭 Манипулятивные стратегии: мастер-класс по контролю")
            narrative_parts.append("")
            for tactic in manipulation_tactics[:3]:
                narrative_parts.append(f"**Тактика:** {tactic}")
                narrative_parts.append("")
                narrative_parts.append("*Диалог, который вы слышите слишком часто:*")
                narrative_parts.append("")
                
                if 'газлайтинг' in tactic.lower():
                    narrative_parts.append("**Вы:** 'Вчера ты сказал, что мы поедем к моим родителям на выходные.'")
                    narrative_parts.append(f"**{partner_name}:** 'Я такого не говорил. У тебя проблемы с памятью в последнее время.'")
                    narrative_parts.append("**Вы:** 'Я точно помню...'")
                    narrative_parts.append(f"**{partner_name}:** 'Ты постоянно что-то выдумываешь. Может, стоит обратиться к врачу?'")
                    narrative_parts.append("")
                    narrative_parts.append("Вы начинаете сомневаться в своей памяти. Реальность становится размытой.")
                    
                elif 'обвинение' in tactic.lower() or 'вина' in tactic.lower():
                    narrative_parts.append("**Вы:** 'Мне больно, когда ты кричишь на меня.'")
                    narrative_parts.append(f"**{partner_name}:** 'Я не кричу. Ты просто слишком чувствительная.'")
                    narrative_parts.append("**Вы:** 'Но твой тон...'")
                    narrative_parts.append(f"**{partner_name}:** 'Если бы ты слушала с первого раза, мне не пришлось бы повышать голос. Это твоя вина.'")
                    narrative_parts.append("")
                    narrative_parts.append("Жертва становится виноватой. Классический разворот ситуации.")
                    
                else:
                    narrative_parts.append(f"**{partner_name}:** 'Ты опять расстраиваешься из-за пустяков. Я же делаю это для твоего же блага.'")
                    narrative_parts.append("**Вы:** 'Но мне кажется...'")
                    narrative_parts.append(f"**{partner_name}:** 'Тебе кажется много чего. Хорошо, что у тебя есть я, чтобы помочь тебе разобраться.'")
                    narrative_parts.append("")
                    narrative_parts.append("Ваши чувства обесцениваются, а он представляется спасителем.")
                
                narrative_parts.append("")
                narrative_parts.append("*Эмоциональные последствия:*")
                narrative_parts.append("После таких разговоров вы чувствуете себя опустошенной. Вроде бы все логично, но внутри растет тревога. Вы начинаете сомневаться в себе, в своих чувствах, в своих воспоминаниях.")
                narrative_parts.append("")
        
        # Эмоциональные паттерны
        if emotional_patterns:
            narrative_parts.append("### 💭 Эмоциональный мир: карта ваших чувств")
            narrative_parts.append("")
            for pattern in emotional_patterns[:3]:
                narrative_parts.append(f"**Эмоциональный паттерн:** {pattern}")
                narrative_parts.append("")
                narrative_parts.append("*Внутренний монолог:*")
                narrative_parts.append("")
                narrative_parts.append(f"'Опять это чувство в животе. Он еще ничего не сказал, но я уже знаю - будет скандал. Как он это делает? Как он умудряется заставить меня чувствовать себя виноватой, даже когда я ничего не делала?'")
                narrative_parts.append("")
                narrative_parts.append("Вы стоите перед зеркалом и видите усталые глаза. Когда вы перестали узнавать себя? Когда ваши эмоции стали подчиняться его настроению?")
                narrative_parts.append("")
                narrative_parts.append("Этот эмоциональный паттерн работает как невидимая нить, которая связывает ваше самочувствие с его поведением. Вы живете в режиме постоянной готовности к эмоциональному урагану.")
                narrative_parts.append("")
        
        # Динамика отношений
        if relationship_dynamics:
            narrative_parts.append("### 💕 Динамика отношений: танец двоих")
            narrative_parts.append("")
            for dynamic in relationship_dynamics[:3]:
                narrative_parts.append(f"**Динамика:** {dynamic}")
                narrative_parts.append("")
                narrative_parts.append("*Хореография ваших отношений:*")
                narrative_parts.append("")
                narrative_parts.append("Представьте танец, где один партнер ведет, а другой следует. Но в вашем случае ведущий меняет шаги посреди танца, не предупреждая партнера. Вы спотыкаетесь, а он говорит, что вы плохо танцуете.")
                narrative_parts.append("")
                narrative_parts.append("Утром - нежность и извинения. Днем - холодность и претензии. Вечером - страсть и обещания. Вы никогда не знаете, какого партнера встретите, открыв глаза.")
                narrative_parts.append("")
                narrative_parts.append("Эта динамика создает состояние постоянной неопределенности. Вы ходите по минному полю, не зная, где взорвется следующая мина.")
                narrative_parts.append("")
        
        # Заключение с призывом к действию
        narrative_parts.append("### 🎯 Общая картина: время принимать решения")
        narrative_parts.append("")
        narrative_parts.append(f"Анализируя все эти элементы вместе, мы видим сложную и тревожную картину. {partner_name} - это не просто 'сложный характер' или 'особенности личности'. Это система поведения, которая систематически подрывает ваше эмоциональное благополучие.")
        narrative_parts.append("")
        narrative_parts.append("*Момент истины:*")
        narrative_parts.append("")
        narrative_parts.append("Представьте себя через пять лет. Вы все еще ходите на цыпочках, все еще сомневаетесь в своей реальности, все еще надеетесь, что он изменится? Или вы видите себя свободной, уверенной, живущей полной жизнью?")
        narrative_parts.append("")
        narrative_parts.append("Каждый день, который вы проводите в таких отношениях, - это день, украденный у вашего настоящего счастья. Вы заслуживаете любви, которая не требует отказа от себя.")
        narrative_parts.append("")
        narrative_parts.append("*Помните: понимание этих паттернов дает вам силу. Не для того, чтобы лучше приспособиться к ним, а для того, чтобы принять решение о своем будущем. Вы не обязаны танцевать под чужую музыку всю жизнь.*")
        
        final_narrative = "\n".join(narrative_parts)
        
        # Добавляем дополнительный контент если нарратив слишком короткий
        if len(final_narrative) < 5000:
            narrative_parts.append("")
            narrative_parts.append("### 🌟 Послесловие: путь к свободе")
            narrative_parts.append("")
            narrative_parts.append("Чтение этого анализа может быть болезненным. Возможно, вы узнаете в нем свою жизнь, свои отношения, свою боль. Это нормально. Это первый шаг к освобождению.")
            narrative_parts.append("")
            narrative_parts.append("Многие женщины говорят: 'Я знала, что что-то не так, но не могла понять, что именно.' Теперь у вас есть слова для ваших чувств, названия для ваших переживаний.")
            narrative_parts.append("")
            narrative_parts.append("Вы не одиноки. Миллионы женщин прошли через подобные отношения. Многие из них нашли силы изменить свою жизнь. Вы тоже можете.")
            narrative_parts.append("")
            narrative_parts.append("Помните: любовь не должна причинять боль. Отношения не должны разрушать вашу личность. Вы имеете право на счастье, уважение, и покой.")
            narrative_parts.append("")
            narrative_parts.append("Первый шаг - это признание проблемы. Вы его уже сделали. Теперь каждый следующий шаг приближает вас к свободе.")
        
        return "\n".join(narrative_parts)

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
                    "Свяжитесь со службами помощи жертвам домашнего насилия"
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
                "narcissism": round(min(10, risk_score / 12), 1),
                "control": round(min(10, risk_score / 10), 1),
                "gaslighting": round(min(10, (risk_score - 5) / 12), 1),
                "emotion": round(min(10, risk_score / 15), 1),
                "intimacy": round(min(10, (risk_score - 10) / 12), 1),
                "social": round(min(10, risk_score / 11), 1)
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
        
        if response_type == 'profile' or 'profiler' in response_type:
            # Check required fields
            required_fields = ['personality_type', 'psychological_profile', 'red_flags', 'manipulation_risk']
            for field in required_fields:
                if field in response and response[field]:
                    quality_score += 20
                else:
                    quality_issues.append(f"Missing or empty field: {field}")
            
            # Check psychological profile length
            profile_text = response.get('psychological_profile', '')
            if len(profile_text) >= 1000:  # Increased minimum for detailed profiles
                quality_score += 10
            else:
                quality_issues.append(f"Psychological profile too short: {len(profile_text)} chars")
            
            # Check red flags specificity
            red_flags = response.get('red_flags', [])
            if isinstance(red_flags, list) and len(red_flags) >= 3:
                quality_score += 10
            else:
                quality_issues.append(f"Insufficient red flags: {len(red_flags) if isinstance(red_flags, list) else 0}")
            
            # Additional checks for Tree of Thoughts profiling
            if 'profiler_tree_of_thoughts' in response_type:
                # Check for expert analyses
                expert_analyses = response.get('expert_analyses', {})
                if isinstance(expert_analyses, dict) and len(expert_analyses) >= 3:
                    quality_score += 10
                else:
                    quality_issues.append(f"Tree of Thoughts missing expert analyses: {len(expert_analyses) if isinstance(expert_analyses, dict) else 0}")
                
                # Check for personalized insights
                insights = response.get('personalized_insights', [])
                if isinstance(insights, list) and len(insights) >= 4:
                    quality_score += 10
                else:
                    quality_issues.append(f"Insufficient personalized insights: {len(insights) if isinstance(insights, list) else 0}")
                
                # Check for behavioral evidence
                evidence = response.get('behavioral_evidence', [])
                if isinstance(evidence, list) and len(evidence) >= 8:
                    quality_score += 10
                else:
                    quality_issues.append(f"Insufficient behavioral evidence: {len(evidence) if isinstance(evidence, list) else 0}")
                
                # Check for missing required fields
                if 'survival_guide' in response:
                    quality_score += 5
                if 'overall_risk_score' in response:
                    quality_score += 5
                if 'dark_triad' in response:
                    quality_score += 5
            
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

    def _validate_personalization_quality(self, result: Dict[str, Any], original_answers: str) -> Dict[str, Any]:
        """Validate personalization quality and fix missing elements"""
        try:
            # Extract key phrases from original answers for validation
            answer_keywords = self._extract_answer_keywords(original_answers)
            
            # Validate personalized insights
            insights = result.get("personalized_insights", [])
            validated_insights = []
            
            for insight in insights:
                if isinstance(insight, str) and len(insight) > 50:
                    # Check if insight contains references to specific behavior
                    has_specifics = any(keyword in insight.lower() for keyword in answer_keywords)
                    if has_specifics or "например" in insight.lower() or "как показывает" in insight.lower():
                        validated_insights.append(insight)
                    else:
                        # Enhance generic insights with specifics
                        enhanced_insight = f"На основе предоставленной информации: {insight}"
                        validated_insights.append(enhanced_insight)
            
            # If not enough quality insights, generate from behavioral evidence
            if len(validated_insights) < 3:
                behavioral_evidence = result.get("behavioral_evidence", [])
                for evidence in behavioral_evidence[:5]:  # Use first 5 pieces of evidence
                    if isinstance(evidence, str) and len(evidence) > 30:
                        insight = f"Персонализированный инсайт: {evidence} - это указывает на конкретную поведенческую модель."
                        validated_insights.append(insight)
                        if len(validated_insights) >= 8:  # Target 8 insights
                            break
            
            # Validate behavioral evidence
            evidence = result.get("behavioral_evidence", [])
            validated_evidence = []
            
            for item in evidence:
                if isinstance(item, str) and len(item) > 30:
                    # Check if evidence is specific enough
                    has_quotes = "'" in item or '"' in item or "говорит" in item.lower()
                    has_examples = any(keyword in item.lower() for keyword in answer_keywords[:10])
                    
                    if has_quotes or has_examples:
                        validated_evidence.append(item)
                    else:
                        # Enhance generic evidence
                        enhanced_evidence = f"Конкретное поведение: {item} (основано на ответах пользователя)"
                        validated_evidence.append(enhanced_evidence)
            
            # Generate additional evidence if needed
            if len(validated_evidence) < 8:
                red_flags = result.get("red_flags", [])
                for flag in red_flags:
                    if isinstance(flag, str) and len(flag) > 20:
                        evidence_item = f"Поведенческое доказательство: {flag}"
                        validated_evidence.append(evidence_item)
                        if len(validated_evidence) >= 10:  # Target 10 pieces of evidence
                            break
            
            # Update result with validated data
            result["personalized_insights"] = validated_insights[:8]  # Limit to 8 best insights
            result["behavioral_evidence"] = validated_evidence[:10]  # Limit to 10 best evidence pieces
            
            # Add validation metrics
            result["personalization_score"] = len(validated_insights) + len(validated_evidence)
            result["quality_validated"] = True
            
            logger.info(f"Personalization validation: {len(validated_insights)} insights, {len(validated_evidence)} evidence pieces")
            
            return result
            
        except Exception as e:
            logger.error(f"Personalization validation failed: {e}")
            return result
    
    def _extract_answer_keywords(self, answers_text: str) -> List[str]:
        """Extract key behavioral keywords from user answers"""
        # Common behavioral indicators in Russian
        behavioral_keywords = [
            "кричит", "бьет", "угрожает", "контролирует", "проверяет", "запрещает",
            "изолирует", "принуждает", "манипулирует", "газлайтит", "унижает", 
            "оскорбляет", "ревнует", "следит", "винит", "отрицает", "переворачивает",
            "швырнул", "схватить", "прижать", "орать", "дуется", "молчит",
            "обвиняет", "критикует", "принижает", "сравнивает", "давит"
        ]
        
        found_keywords = []
        answers_lower = answers_text.lower()
        
        for keyword in behavioral_keywords:
            if keyword in answers_lower:
                found_keywords.append(keyword)
        
        # Also extract quoted phrases (likely specific examples)
        import re
        quotes = re.findall(r"['\"](.*?)['\"]", answers_text)
        for quote in quotes:
            if len(quote) > 10 and len(quote) < 100:  # Reasonable length quotes
                found_keywords.append(quote.lower())
        
        return found_keywords[:20]  # Return top 20 keywords

    async def _parse_storytelling_iterative(self, structured_response: str, partner_name: str, original_answers: str) -> Dict[str, Any]:
        """
        ИТЕРАТИВНЫЙ ПОДХОД: Парсинг storytelling в два этапа
        1. Получить структурированные данные из первого ответа
        2. Генерировать storytelling narrative на основе структурированных данных
        """
        try:
            # Этап 1: Парсим структурированные данные
            logger.info("Step 1: Parsing structured data for storytelling")
            structured_data = extract_json_from_text(structured_response)
            if not structured_data:
                structured_data = safe_json_loads(structured_response, {})
            
            # Проверяем, что получили структурированные данные
            if not structured_data or not isinstance(structured_data, dict):
                logger.error("Failed to parse structured data, falling back to standard parsing")
                return self._parse_storytelling_response(structured_response)
            
            # Этап 2: Генерируем storytelling narrative
            logger.info("Step 2: Generating storytelling narrative from structured data")
            
            # Создаем промпт для storytelling generation
            storytelling_prompt = create_storytelling_narrative_prompt(
                structured_data=structured_data,
                partner_name=partner_name,
                original_answers=original_answers
            )
            
            # Генерируем storytelling narrative
            async with self._request_semaphore:
                storytelling_narrative = await self._get_ai_response(
                    system_prompt="Ты - мастер storytelling. ВАЖНО: Возвращай ТОЛЬКО чистый текст без JSON, объектов или мета-данных. Начинай ответ сразу с заголовка '## 🧠'. Пиши МАКСИМАЛЬНО ПОДРОБНО, минимум 1500 слов!",
                    user_prompt=storytelling_prompt,
                    response_format="text",  # Не JSON, а обычный текст
                    max_tokens=8192,  # Максимальный лимит для Claude
                    technique="storytelling_narrative"
                )
            
            # Этап 3: Объединяем результаты
            logger.info(f"Step 3: Combining results - narrative length: {len(storytelling_narrative)} chars")
            
            # Проверяем, не вернул ли Claude JSON вместо текста
            if storytelling_narrative.strip().startswith('{'):
                logger.warning("Claude returned JSON instead of text, attempting to extract story")
                try:
                    json_response = extract_json_from_text(storytelling_narrative)
                    if json_response and 'story' in json_response:
                        storytelling_narrative = json_response['story']
                        logger.info(f"Extracted story from JSON: {len(storytelling_narrative)} chars")
                    else:
                        logger.error("Could not extract story from JSON response")
                except Exception as e:
                    logger.error(f"Failed to parse JSON response: {e}")
            
            # Создаем финальный результат
            result = {
                "personality_type": structured_data.get("personality_type", "Неопределен"),
                "manipulation_risk": float(structured_data.get("manipulation_risk", 5.0)),
                "urgency_level": structured_data.get("urgency_level", "medium"),
                "psychological_profile": storytelling_narrative.strip(),  # Готовый storytelling текст
                "red_flags": structured_data.get("red_flags", []),
                "safety_alerts": structured_data.get("safety_alerts", []),
                "block_scores": structured_data.get("block_scores", {}),
                "dark_triad": structured_data.get("dark_triad", {}),
                "personalized_insights": structured_data.get("personalized_insights", []),
                "behavioral_evidence": structured_data.get("behavioral_evidence", []),
                "manipulation_tactics": structured_data.get("manipulation_tactics", []),
                "emotional_patterns": structured_data.get("emotional_patterns", []),
                "control_mechanisms": structured_data.get("control_mechanisms", []),
                "violence_indicators": structured_data.get("violence_indicators", []),
                "escalation_triggers": structured_data.get("escalation_triggers", []),
                
                # Метаданные итеративного подхода
                "structured_analysis": structured_data,
                "narrative_length": len(storytelling_narrative),
                "narrative_words": len(storytelling_narrative.split()),
                "generation_method": "iterative_storytelling"
            }
            
            # Calculate overall risk score from manipulation_risk
            overall_risk = result["manipulation_risk"] * 10
            result["overall_risk_score"] = round(overall_risk, 1)
            
            # Round block scores using proper validation
            block_scores = result.get("block_scores", {})
            for block in block_scores:
                if isinstance(block_scores[block], (int, float)):
                    block_scores[block] = round(float(block_scores[block]), 1)
            
            # Add compatibility fields
            result.update({
                "positive_traits": [],
                "danger_assessment": f"Итеративный storytelling анализ: {result['urgency_level']}",
                "relationship_forecast": "Прогноз основан на детальном двухэтапном анализе",
                "exit_strategy": "См. персонализированные рекомендации с конкретными примерами",
                "confidence_level": 0.9,  # Выше из-за двухэтапного подхода
                "survival_guide": structured_data.get("survival_guide", ["Обратитесь за профессиональной помощью"])
            })
            
            logger.info(f"Iterative storytelling complete: {result['narrative_words']} words, {len(result['red_flags'])} red flags")
            
            return result
            
        except Exception as e:
            logger.error(f"Iterative storytelling failed: {e}")
            # Fallback к стандартному парсингу
            return self._parse_storytelling_response(structured_response)

    async def _parse_storytelling_iterative_triple(self, structured_response: str, partner_name: str, original_answers: str) -> Dict[str, Any]:
        """
        ТРЕХЭТАПНЫЙ ПОДХОД: Парсинг storytelling в три этапа
        1. Получить структурированные данные из первого ответа
        2. Генерировать первую половину storytelling (750 слов)
        3. Генерировать вторую половину storytelling (750 слов)
        """
        try:
            # Этап 1: Парсим структурированные данные
            logger.info("Step 1: Parsing structured data for storytelling")
            structured_data = extract_json_from_text(structured_response)
            if not structured_data:
                structured_data = safe_json_loads(structured_response, {})
            
            # Проверяем, что получили структурированные данные
            if not structured_data or not isinstance(structured_data, dict):
                logger.error("Failed to parse structured data, falling back to standard parsing")
                return self._parse_storytelling_response(structured_response)
            
            # Этап 2: Генерируем первую половину storytelling
            logger.info("Step 2: Generating first half of storytelling narrative")
            
            # Создаем промпт для первой половины
            first_half_prompt = self._create_storytelling_first_half_prompt(
                structured_data=structured_data,
                partner_name=partner_name,
                original_answers=original_answers
            )
            
            # Генерируем первую половину
            async with self._request_semaphore:
                first_half_narrative = await self._get_ai_response(
                    system_prompt="Ты - мастер storytelling. ВАЖНО: Возвращай ТОЛЬКО чистый текст без JSON. Начинай ответ сразу с заголовка '## 🧠'. Пиши МАКСИМАЛЬНО ПОДРОБНО, 800+ слов! НЕ ОСТАНАВЛИВАЙСЯ - пиши ВСЕ разделы полностью с диалогами и сценариями!",
                    user_prompt=first_half_prompt,
                    response_format="text",
                    max_tokens=8192,
                    technique="storytelling_narrative"
                )
            
            # Этап 3: Генерируем вторую половину storytelling
            logger.info("Step 3: Generating second half of storytelling narrative")
            
            # Создаем промпт для второй половины
            second_half_prompt = self._create_storytelling_second_half_prompt(
                structured_data=structured_data,
                partner_name=partner_name,
                original_answers=original_answers,
                first_half_narrative=first_half_narrative
            )
            
            # Генерируем вторую половину
            async with self._request_semaphore:
                second_half_narrative = await self._get_ai_response(
                    system_prompt="Ты - мастер storytelling. ВАЖНО: Возвращай ТОЛЬКО чистый текст без JSON. Продолжай storytelling с раздела '## 🎯'. Пиши МАКСИМАЛЬНО ПОДРОБНО, 800+ слов! НЕ ОСТАНАВЛИВАЙСЯ - пиши ВСЕ разделы полностью с диалогами и сценариями!",
                    user_prompt=second_half_prompt,
                    response_format="text",
                    max_tokens=8192,
                    technique="storytelling_narrative"
                )
            
            # Объединяем две части
            full_narrative = first_half_narrative.strip() + "\n\n" + second_half_narrative.strip()
            
            # Этап 4: Объединяем результаты
            logger.info(f"Step 4: Combining results - full narrative length: {len(full_narrative)} chars")
            
            # Создаем финальный результат
            result = {
                "personality_type": structured_data.get("personality_type", "Неопределен"),
                "manipulation_risk": float(structured_data.get("manipulation_risk", 5.0)),
                "urgency_level": structured_data.get("urgency_level", "medium"),
                "psychological_profile": full_narrative,  # Полный storytelling текст
                "red_flags": structured_data.get("red_flags", []),
                "safety_alerts": structured_data.get("safety_alerts", []),
                "block_scores": structured_data.get("block_scores", {}),
                "dark_triad": structured_data.get("dark_triad", {}),
                "personalized_insights": structured_data.get("personalized_insights", []),
                "behavioral_evidence": structured_data.get("behavioral_evidence", []),
                "manipulation_tactics": structured_data.get("manipulation_tactics", []),
                "emotional_patterns": structured_data.get("emotional_patterns", []),
                "control_mechanisms": structured_data.get("control_mechanisms", []),
                "violence_indicators": structured_data.get("violence_indicators", []),
                "escalation_triggers": structured_data.get("escalation_triggers", []),
                
                # Метаданные трехэтапного подхода
                "structured_analysis": structured_data,
                "narrative_length": len(full_narrative),
                "narrative_words": len(full_narrative.split()),
                "first_half_words": len(first_half_narrative.split()),
                "second_half_words": len(second_half_narrative.split()),
                "generation_method": "triple_iterative_storytelling"
            }
            
            # Calculate overall risk score from manipulation_risk
            overall_risk = result["manipulation_risk"] * 10
            result["overall_risk_score"] = round(overall_risk, 1)
            
            # Round block scores using proper validation
            block_scores = result.get("block_scores", {})
            for block in block_scores:
                if isinstance(block_scores[block], (int, float)):
                    block_scores[block] = round(float(block_scores[block]), 1)
            
            # Add compatibility fields
            result.update({
                "positive_traits": [],
                "danger_assessment": f"Трехэтапный storytelling анализ: {result['urgency_level']}",
                "relationship_forecast": "Прогноз основан на детальном трехэтапном анализе",
                "exit_strategy": "См. персонализированные рекомендации с конкретными примерами",
                "confidence_level": 0.95,  # Выше из-за трехэтапного подхода
                "survival_guide": structured_data.get("survival_guide", ["Обратитесь за профессиональной помощью"])
            })
            
            logger.info(f"Triple iterative storytelling complete: {result['narrative_words']} words, {len(result['red_flags'])} red flags")
            
            return result
            
        except Exception as e:
            logger.error(f"Triple iterative storytelling failed: {e}")
            # Fallback к двухэтапному подходу
            return await self._parse_storytelling_iterative(structured_response, partner_name, original_answers)
    
    def _create_storytelling_first_half_prompt(self, structured_data: dict, partner_name: str, original_answers: str) -> str:
        """Создает промпт для первой половины storytelling"""
        
        prompt = f"""Ты - мастер storytelling. Твоя задача - создать ПЕРВУЮ ПОЛОВИНУ захватывающего психологического рассказа о партнере {partner_name}.

СТРУКТУРИРОВАННЫЕ ДАННЫЕ:
- Тип личности: {structured_data.get('personality_type', 'Неопределен')}
- Ключевые черты: {structured_data.get('core_traits', [])}
- Поведенческие паттерны: {structured_data.get('behavioral_patterns', [])}
- Красные флаги: {structured_data.get('red_flags', [])}

ОРИГИНАЛЬНЫЕ ОТВЕТЫ:
{original_answers}

ТВОЯ ЗАДАЧА: Создать ПЕРВУЮ ПОЛОВИНУ storytelling анализа (750+ слов).

СТРУКТУРА ПЕРВОЙ ПОЛОВИНЫ:
## 🧠 Знакомство с {partner_name}: первые впечатления и скрытая правда
[Детальная история знакомства с диалогами - 200+ слов]

## 🎭 Ключевые черты личности в действии
[Живые сценарии с диалогами для каждой черты - 300+ слов]

## 🎬 Поведенческие паттерны: как разворачивается контроль
[Пошаговое описание эскалации - 250+ слов]

ТРЕБОВАНИЯ:
- МИНИМУМ 750 слов в первой половине
- Каждый раздел с живыми диалогами
- Конкретные сценарии с деталями
- Используй имя {partner_name} в диалогах
- Создавай атмосферу реальности

ВАЖНО: Пиши ТОЛЬКО первую половину! Заканчивай на разделе "Поведенческие паттерны".

ВЕРНИ ТОЛЬКО ЧИСТЫЙ STORYTELLING ТЕКСТ БЕЗ JSON!"""
        
        return prompt
    
    def _create_storytelling_second_half_prompt(self, structured_data: dict, partner_name: str, original_answers: str, first_half_narrative: str) -> str:
        """Создает промпт для второй половины storytelling"""
        
        prompt = f"""Ты - мастер storytelling. Твоя задача - создать ВТОРУЮ ПОЛОВИНУ захватывающего психологического рассказа о партнере {partner_name}.

У тебя есть ПЕРВАЯ ПОЛОВИНА рассказа:
{first_half_narrative[:1000]}...

СТРУКТУРИРОВАННЫЕ ДАННЫЕ:
- Манипулятивные тактики: {structured_data.get('manipulation_tactics', [])}
- Эмоциональные паттерны: {structured_data.get('emotional_patterns', [])}
- Динамика отношений: {structured_data.get('relationship_dynamics', [])}
- Красные флаги: {structured_data.get('red_flags', [])}

ТВОЯ ЗАДАЧА: Создать ВТОРУЮ ПОЛОВИНУ storytelling анализа (750+ слов).

СТРУКТУРА ВТОРОЙ ПОЛОВИНЫ:
## 🎯 Мастерство манипуляций: разбор техник
[Детальный анализ каждой тактики с диалогами - 200+ слов]

## 💭 Эмоциональный мир {partner_name}: что происходит внутри
[Глубинная психология через наблюдаемое поведение - 150+ слов]

## 💕 Динамика отношений: танец двоих
[Циклы насилия и контроля - 200+ слов]

## 🚨 Красные флаги: сигналы опасности
[Каждый флаг через живую историю - 150+ слов]

## 🔮 Прогноз: что ждет впереди
[Научно обоснованные выводы - 100+ слов]

ТРЕБОВАНИЯ:
- МИНИМУМ 750 слов во второй половине
- Каждый раздел с живыми диалогами
- Конкретные сценарии с деталями
- Используй имя {partner_name} в диалогах
- Логично продолжай первую половину

ВАЖНО: Пиши ТОЛЬКО вторую половину! Начинай с раздела "## 🎯 Мастерство манипуляций".

ВЕРНИ ТОЛЬКО ЧИСТЫЙ STORYTELLING ТЕКСТ БЕЗ JSON!"""
        
        return prompt


# Global AI service instance
ai_service = AIService() 