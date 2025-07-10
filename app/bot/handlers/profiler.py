"""Partner profiler handler - FULL version (28 questions, 6 blocks)"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.utils.decorators import handle_errors
from app.bot.keyboards.inline import (
    profiler_menu_kb, back_to_main_kb, profiler_full_navigation_kb,
    profiler_results_navigation_kb, profiler_block_analysis_kb,
    profiler_safety_plan_kb, profiler_my_profiles_kb, 
    profiler_confirmation_kb, profiler_progress_visual_kb
)
from app.bot.states import PartnerProfileStates
from app.services.user_service import UserService
from app.services.ai_service import ai_service
from app.core.database import get_session
from app.core.logging import logger
from app.prompts.profiler_full_questions import (
    get_question_by_state, get_next_question_state, get_previous_question_state,
    get_question_progress, format_question_text, calculate_weighted_scores,
    get_safety_alerts, validate_full_answers, get_all_questions, QUESTION_ORDER,
    get_block_by_question
)
from app.prompts.profiler_full_prompts import (
    get_profiler_full_analysis_prompt, get_safety_assessment_prompt,
    get_relationship_therapy_prompt, get_patterns_recognition_prompt
)
import json

router = Router()

@router.callback_query(F.data == "profiler_menu")
@handle_errors
async def show_profiler_menu(callback: CallbackQuery):
    """Show partner profiler menu"""
    menu_text = """
👤 **Профиль партнера** *(Полная версия)*

Создайте комплексный психологический портрет партнера для анализа отношений:

🆕 **Новый профиль** - пройти анкету (28 вопросов)
📋 **Мои профили** - просмотр созданных профилей
🎯 **Рекомендации** - персональные советы по безопасности

💡 **Научно обоснованная анкета включает:**
• 🧠 Нарциссизм и грандиозность (6 вопросов)
• 🎯 Контроль и манипуляции (6 вопросов)
• 🔄 Газлайтинг и искажение реальности (5 вопросов)
• 💭 Эмоциональная регуляция (4 вопроса)
• 💕 Интимность и принуждение (3 вопроса)
• 👥 Социальное поведение (4 вопроса)

🔬 **Основано на:** Dark Triad, DSM-5, Duluth Model

Что вас интересует?
"""
    
    await callback.message.edit_text(
        menu_text,
        reply_markup=profiler_menu_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "create_profile")
@handle_errors
async def create_profile(callback: CallbackQuery, state: FSMContext):
    """Start profile creation"""
    await state.set_state(PartnerProfileStates.waiting_for_name)
    
    intro_text = """🆕 **Создание профиля партнера** *(Полная версия)*

Давайте создадим комплексный психологический портрет вашего партнера для анализа отношений.

📋 **Процесс включает:**
• Имя и описание партнера
• 28 научно обоснованных вопросов в 6 блоках
• AI-анализ с использованием продвинутых алгоритмов
• Детальные рекомендации по безопасности
• Прогноз развития отношений

🔬 **Научная основа:** Dark Triad, DSM-5, Duluth Model

⚠️ **Важно:** Все данные конфиденциальны и используются только для анализа.

👤 **Как зовут вашего партнера?**
*(Введите имя или псевдоним)*"""

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❌ Отменить", callback_data="profiler_menu")
    )
    
    await callback.message.edit_text(
        intro_text,
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(PartnerProfileStates.waiting_for_name)
@handle_errors
async def process_partner_name(message: Message, state: FSMContext):
    """Process partner name input"""
    partner_name = message.text.strip()
    
    if len(partner_name) < 1 or len(partner_name) > 50:
        await message.answer(
            "❌ Имя должно содержать от 1 до 50 символов. Попробуйте ещё раз:",
            parse_mode="Markdown"
        )
        return
    
    await state.update_data(partner_name=partner_name)
    await state.set_state(PartnerProfileStates.waiting_for_description)
    
    description_text = f"""✅ **Партнер:** {partner_name}

📝 **Краткое описание**

Опишите вашего партнера в свободной форме (2-3 предложения):
• Основные черты характера
• Как он/она ведет себя в отношениях
• Ваши общие впечатления

💡 *Это поможет AI лучше понять контекст для анализа*

*(Максимум 500 символов)*"""

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⏭️ Пропустить", callback_data="skip_description"),
        InlineKeyboardButton(text="❌ Отменить", callback_data="profiler_menu")
    )
    
    await message.answer(
        description_text,
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@router.message(PartnerProfileStates.waiting_for_description)
@handle_errors
async def process_partner_description(message: Message, state: FSMContext):
    """Process partner description"""
    description = message.text.strip()
    
    if len(description) > 500:
        await message.answer(
            "❌ Описание не должно превышать 500 символов. Попробуйте сократить:",
            parse_mode="Markdown"
        )
        return
    
    await state.update_data(partner_description=description)
    await start_questionnaire(message, state)

@router.callback_query(F.data == "skip_description", PartnerProfileStates.waiting_for_description)
@handle_errors
async def skip_description(callback: CallbackQuery, state: FSMContext):
    """Skip description and start questionnaire"""
    await state.update_data(partner_description="")
    await start_questionnaire(callback.message, state)
    await callback.answer()

async def start_questionnaire(message: Message, state: FSMContext):
    """Start the full questionnaire (28 questions)"""
    await state.set_state(PartnerProfileStates.narcissism_q1)
    await state.update_data(answers={})
    
    data = await state.get_data()
    partner_name = data.get("partner_name", "партнер")
    
    intro_text = f"""📋 **Анкета о партнере "{partner_name}"** *(Полная версия)*

Теперь ответьте на 28 научно обоснованных вопросов о поведении вашего партнера.

🎯 **6 блоков анализа:**
🧠 Нарциссизм и грандиозность (6 вопросов)
🎯 Контроль и манипуляции (6 вопросов)
🔄 Газлайтинг и искажение реальности (5 вопросов)
💭 Эмоциональная регуляция (4 вопроса)
💕 Интимность и принуждение (3 вопроса)
👥 Социальное поведение (4 вопроса)

🔬 **Научная основа:** Dark Triad, DSM-5, Duluth Model

💡 **Отвечайте максимально честно - качество анализа зависит от точности ваших ответов.**

⏱️ **Время прохождения:** ~10-15 минут

Начинаем с первого вопроса:"""
    
    await message.answer(intro_text, parse_mode="Markdown")
    await show_question(message, state, "narcissism_q1")

async def show_question(message: Message, state: FSMContext, question_state: str):
    """Show a questionnaire question with enhanced UI"""
    question_data = get_question_by_state(question_state)
    if not question_data:
        logger.error(f"Question data not found for state: {question_state}")
        return
    
    current_num, total_questions = get_question_progress(question_state)
    block_name = get_block_by_question(question_state)
    
    # Enhanced question text with visual elements
    question_text = format_question_text(question_data, current_num, total_questions)
    
    # Visual progress bar
    progress_filled = int((current_num / total_questions) * 20)
    progress_bar = "█" * progress_filled + "░" * (20 - progress_filled)
    
    enhanced_text = f"""{question_text}

📊 **Прогресс:** {progress_bar} {current_num}/{total_questions}
🏷️ **Блок:** {block_name}"""
    
    # Create answer buttons
    builder = InlineKeyboardBuilder()
    
    # Add answer options with enhanced formatting
    for i, option in enumerate(question_data['options']):
        # Smart truncation preserving meaning
        if len(option) > 45:
            # Find last space before limit
            truncate_pos = option.rfind(' ', 0, 42)
            button_text = option[:truncate_pos] + "..." if truncate_pos > 20 else option[:42] + "..."
        else:
            button_text = option
        
        # Add option indicators
        option_emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"][i] if i < 5 else f"{i+1}️⃣"
        
        builder.row(
            InlineKeyboardButton(
                text=f"{option_emoji} {button_text}",
                callback_data=f"answer_{question_state}_{i}"
            )
        )
    
    # Enhanced navigation
    nav_buttons = []
    
    # Previous button with smart text
    if current_num > 1:
        nav_buttons.append(
            InlineKeyboardButton(text="⬅️ Предыдущий", callback_data=f"prev_{question_state}")
        )
    
    # Progress button with percentage
    progress_percent = int((current_num / total_questions) * 100)
    nav_buttons.append(
        InlineKeyboardButton(
            text=f"📊 {progress_percent}% ({current_num}/{total_questions})", 
            callback_data="prof_progress_visual"
        )
    )
    
    # Skip button for non-critical questions
    if question_data.get('weight', 2) < 4:  # Not critical
        nav_buttons.append(
            InlineKeyboardButton(text="⏭️ Пропустить", callback_data=f"prof_skip_{question_state}")
        )
    
    if nav_buttons:
        builder.row(*nav_buttons)
    
    # Block info button
    block_emoji = {
        "Нарциссизм и грандиозность": "🧠",
        "Контроль и манипуляции": "🎯", 
        "Газлайтинг и искажение реальности": "🔄",
        "Эмоциональная регуляция": "💭",
        "Интимность и принуждение": "💕",
        "Социальное поведение": "👥"
    }.get(block_name, "📋")
    
    builder.row(
        InlineKeyboardButton(
            text=f"{block_emoji} О блоке: {block_name}", 
            callback_data=f"prof_block_info_{question_state}"
        )
    )
    
    # Enhanced action buttons
    action_buttons = []
    action_buttons.append(
        InlineKeyboardButton(text="💾 Сохранить прогресс", callback_data="prof_save_progress")
    )
    action_buttons.append(
        InlineKeyboardButton(text="❌ Выйти", callback_data="prof_exit_confirm")
    )
    
    builder.row(*action_buttons)
    
    await message.answer(
        enhanced_text,
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("answer_"))
@handle_errors
async def process_answer(callback: CallbackQuery, state: FSMContext):
    """Process question answer"""
    # Parse callback data: answer_{question_state}_{answer_index}
    parts = callback.data.split("_", 2)
    if len(parts) != 3:
        await callback.answer("❌ Ошибка обработки ответа")
        return
    
    question_state = parts[1] + "_" + parts[2].split("_")[0] + "_" + parts[2].split("_")[1]
    answer_index = int(parts[2].split("_")[2])
    
    # Save answer
    data = await state.get_data()
    answers = data.get("answers", {})
    answers[question_state] = answer_index
    await state.update_data(answers=answers)
    
    # Get next question
    next_state = get_next_question_state(question_state)
    
    if next_state == "reviewing_answers":
        await show_review(callback.message, state)
    else:
        # Set next state and show next question
        await state.set_state(getattr(PartnerProfileStates, next_state))
        await show_question(callback.message, state, next_state)
    
    await callback.answer()

@router.callback_query(F.data.startswith("prev_"))
@handle_errors
async def go_to_previous_question(callback: CallbackQuery, state: FSMContext):
    """Go to previous question"""
    current_state = callback.data.replace("prev_", "")
    prev_state = get_previous_question_state(current_state)
    
    if prev_state == "waiting_for_description":
        await state.set_state(PartnerProfileStates.waiting_for_description)
        await callback.message.edit_text(
            "📝 Вернулись к описанию партнера. Вы можете изменить описание или продолжить с вопросами.",
            parse_mode="Markdown"
        )
    else:
        await state.set_state(getattr(PartnerProfileStates, prev_state))
        await show_question(callback.message, state, prev_state)
    
    await callback.answer()

async def show_review(message: Message, state: FSMContext):
    """Show answers review before analysis"""
    await state.set_state(PartnerProfileStates.reviewing_answers)
    
    data = await state.get_data()
    partner_name = data.get("partner_name", "партнер")
    answers = data.get("answers", {})
    
    # Calculate preliminary risk scores with weighted scoring
    weighted_scores = calculate_weighted_scores(answers)
    safety_alerts = get_safety_alerts(answers)
    
    review_text = f"""📋 **Анкета завершена!**

👤 **Партнер:** {partner_name}
📊 **Ответов получено:** {len(answers)}/28

**Предварительная оценка:**
🧠 Нарциссизм: {weighted_scores['block_scores'].get('narcissism', 0):.1f}/10
🎯 Контроль: {weighted_scores['block_scores'].get('control', 0):.1f}/10
🔄 Газлайтинг: {weighted_scores['block_scores'].get('gaslighting', 0):.1f}/10
💭 Эмоциональная регуляция: {weighted_scores['block_scores'].get('emotion', 0):.1f}/10
💕 Интимность: {weighted_scores['block_scores'].get('intimacy', 0):.1f}/10
👥 Социальное поведение: {weighted_scores['block_scores'].get('social', 0):.1f}/10

**Общий уровень риска:** {weighted_scores['overall_risk_score']:.1f}%"""

    # Add safety alerts if any
    if safety_alerts:
        review_text += "\n\n⚠️ **ПРЕДУПРЕЖДЕНИЯ БЕЗОПАСНОСТИ:**\n"
        for alert in safety_alerts:
            review_text += f"• {alert}\n"
    
    review_text += """\n\n🤖 **Следующий шаг:** Запустить AI-анализ для получения детального психологического профиля и рекомендаций.

Продолжить анализ?"""

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🤖 Запустить анализ", callback_data="start_analysis"),
        InlineKeyboardButton(text="✏️ Изменить ответы", callback_data="edit_answers")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Отменить", callback_data="profiler_menu")
    )
    
    await message.answer(
        review_text,
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "start_analysis", PartnerProfileStates.reviewing_answers)
@handle_errors
async def start_ai_analysis(callback: CallbackQuery, state: FSMContext):
    """Start AI analysis of the profile"""
    await callback.answer()
    
    data = await state.get_data()
    partner_name = data.get("partner_name", "партнер")
    partner_description = data.get("partner_description", "")
    answers = data.get("answers", {})
    
    # Validate answers
    is_valid, error_msg = validate_full_answers(answers)
    if not is_valid:
        await callback.message.edit_text(
            f"❌ **Ошибка валидации:**\n{error_msg}\n\nПопробуйте заново.",
            reply_markup=back_to_main_kb(),
            parse_mode="Markdown"
        )
        await state.clear()
        return
    
    # Show processing message
    processing_text = f"""🤖 **Анализ профиля "{partner_name}"**

⚙️ AI обрабатывает ваши ответы...
🧠 Создается психологический профиль...
🔍 Выявляются поведенческие паттерны...
⚠️ Оценивается уровень безопасности...

Это займет 15-30 секунд."""

    await callback.message.edit_text(
        processing_text,
        parse_mode="Markdown"
    )
    
    try:
        # Get AI service and analyze        
        async with get_session() as session:
            user_service = UserService(session)
            user = await user_service.get_user_by_telegram_id(callback.from_user.id)
            
            if not user:
                await callback.message.edit_text(
                    "❌ Пользователь не найден. Используйте /start для регистрации.",
                    reply_markup=back_to_main_kb()
                )
                await state.clear()
                return
            
            # Call AI analysis with full profiler
            analysis_result = await ai_service.profile_partner(
                answers=answers,
                user_id=user.id,
                partner_name=partner_name,
                partner_description=partner_description
            )
            
            # Save results to state for display
            await state.update_data(analysis_result=analysis_result)
            await state.set_state(PartnerProfileStates.profile_complete)
            
            # Show results
            await show_analysis_results(callback.message, state)
            
    except Exception as e:
        logger.error(f"Error in AI analysis: {e}")
        await callback.message.edit_text(
            "❌ **Ошибка анализа**\n\n"
            "Произошла ошибка при обработке профиля. "
            "Попробуйте создать профиль заново или обратитесь в поддержку.",
            reply_markup=back_to_main_kb(),
            parse_mode="Markdown"
        )
        await state.clear()

async def show_analysis_results(message: Message, state: FSMContext):
    """Show AI analysis results"""
    data = await state.get_data()
    partner_name = data.get("partner_name", "партнер")
    analysis = data.get("analysis_result", {})
    
    if not analysis:
        await message.edit_text(
            "❌ Результаты анализа недоступны",
            reply_markup=back_to_main_kb()
        )
        return
    
    # Format results display
    overall_risk = analysis.get("overall_risk_score", 0)
    urgency = analysis.get("urgency_level", "LOW")
    
    # Risk level emoji and text
    risk_emoji = "🟢" if overall_risk < 25 else "🟡" if overall_risk < 50 else "🟠" if overall_risk < 75 else "🔴"
    urgency_text = {
        "LOW": "Низкий", 
        "MEDIUM": "Средний", 
        "HIGH": "Высокий", 
        "CRITICAL": "Критический"
    }.get(urgency, urgency)
    
    results_text = f"""🎯 **Анализ профиля "{partner_name}"** *(Полная версия)*

{risk_emoji} **Общий уровень риска:** {overall_risk:.1f}%
📊 **Категория:** {urgency_text}

🔬 **Оценка по научным блокам:**"""
    
    # Add block scores with new structure
    block_scores = analysis.get("block_scores", {})
    block_emoji = {
        "narcissism": "🧠",
        "control": "🎯", 
        "gaslighting": "🔄",
        "emotion": "💭",
        "intimacy": "💕",
        "social": "👥"
    }
    
    block_names = {
        "narcissism": "Нарциссизм и грандиозность",
        "control": "Контроль и манипуляции",
        "gaslighting": "Газлайтинг и искажение реальности",
        "emotion": "Эмоциональная регуляция",
        "intimacy": "Интимность и принуждение",
        "social": "Социальное поведение"
    }
    
    for block_key, score in block_scores.items():
        emoji = block_emoji.get(block_key, "📊")
        name = block_names.get(block_key, block_key)
        level = "высокий" if score >= 7 else "средний" if score >= 4 else "низкий"
        results_text += f"\n{emoji} {name}: {score:.1f}/10 ({level})"
    
    # Add safety alerts
    safety_alerts = analysis.get("safety_alerts", [])
    if safety_alerts:
        results_text += "\n\n⚠️ **ПРЕДУПРЕЖДЕНИЯ БЕЗОПАСНОСТИ:**"
        for alert in safety_alerts[:3]:  # Показываем первые 3
            results_text += f"\n• {alert}"
    
    # Extract key insights from AI analysis text
    ai_analysis = analysis.get("analysis", "")
    if ai_analysis and len(ai_analysis) > 200:
        # Extract first paragraph as summary
        first_paragraph = ai_analysis.split('\n\n')[0] if '\n\n' in ai_analysis else ai_analysis[:300]
        if len(first_paragraph) > 200:
            first_paragraph = first_paragraph[:200] + "..."
        results_text += f"\n\n💡 **Краткий анализ:**\n{first_paragraph}"
    
    results_text += "\n\n📖 Нажмите кнопки ниже для подробной информации:"

    # Use enhanced results navigation
    await message.edit_text(
        results_text,
        reply_markup=profiler_results_navigation_kb(
            urgency_level=urgency,
            has_safety_alerts=bool(safety_alerts),
            overall_risk=overall_risk
        ),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "detailed_analysis", PartnerProfileStates.profile_complete)
@handle_errors
async def show_detailed_analysis(callback: CallbackQuery, state: FSMContext):
    """Show detailed analysis results"""
    data = await state.get_data()
    analysis = data.get("analysis_result", {})
    partner_name = data.get("partner_name", "партнер")
    
    if not analysis:
        await callback.answer("❌ Данные анализа недоступны")
        return
    
    # Format detailed analysis
    block_analysis = analysis.get("block_analysis", {})
    
    detailed_text = f"""📊 **Детальный анализ "{partner_name}"**

🔍 **Психологический профиль:**
{analysis.get("psychological_profile", "Данные недоступны")}

📈 **Анализ по блокам:**"""
    
    # Add detailed block analysis
    block_titles = {
        "narcissism": "🎭 Нарциссизм",
        "control": "⚖️ Контроль", 
        "gaslighting": "🌀 Газлайтинг",
        "emotional_manipulation": "🎭 Эмоциональные манипуляции",
        "safety": "⚠️ Безопасность"
    }
    
    for block_key, block_data in block_analysis.items():
        if isinstance(block_data, dict):
            title = block_titles.get(block_key, block_key)
            score = block_data.get("score", 0)
            level = block_data.get("level", "неизвестно")
            patterns = block_data.get("key_patterns", [])
            evidence = block_data.get("evidence", "")
            
            detailed_text += f"\n\n{title}: {score:.1f}/10 ({level})"
            if patterns:
                detailed_text += f"\n• Паттерны: {', '.join(patterns[:2])}"
            if evidence:
                detailed_text += f"\n• {evidence[:100]}..."
    
    # Add risk factors
    risk_factors = analysis.get("risk_factors", [])
    if risk_factors:
        detailed_text += f"\n\n⚠️ **Факторы риска:**"
        for factor in risk_factors[:3]:
            detailed_text += f"\n• {factor}"
    
    # Add protective factors
    protective_factors = analysis.get("protective_factors", [])
    if protective_factors:
        detailed_text += f"\n\n✅ **Защитные факторы:**"
        for factor in protective_factors[:3]:
            detailed_text += f"\n• {factor}"
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к результатам", callback_data="back_to_results"),
        InlineKeyboardButton(text="💡 Рекомендации", callback_data="recommendations")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    await callback.message.edit_text(
        detailed_text,
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "recommendations", PartnerProfileStates.profile_complete)
@handle_errors
async def show_recommendations(callback: CallbackQuery, state: FSMContext):
    """Show recommendations and advice"""
    data = await state.get_data()
    analysis = data.get("analysis_result", {})
    partner_name = data.get("partner_name", "партнер")
    
    if not analysis:
        await callback.answer("❌ Данные анализа недоступны")
        return
    
    urgency = analysis.get("urgency_level", "MEDIUM")
    
    recommendations_text = f"""💡 **Рекомендации для отношений с "{partner_name}"**

📊 **Уровень риска:** {urgency}

🎯 **Немедленные действия:**"""
    
    # Add immediate recommendations
    immediate_recs = analysis.get("immediate_recommendations", [])
    for rec in immediate_recs:
        recommendations_text += f"\n• {rec}"
    
    # Add communication advice
    comm_advice = analysis.get("communication_advice", [])
    if comm_advice:
        recommendations_text += f"\n\n💬 **Советы по общению:**"
        for advice in comm_advice:
            recommendations_text += f"\n• {advice}"
    
    # Add long-term recommendations
    long_term_recs = analysis.get("long_term_recommendations", [])
    if long_term_recs:
        recommendations_text += f"\n\n📅 **Долгосрочные рекомендации:**"
        for rec in long_term_recs:
            recommendations_text += f"\n• {rec}"
    
    # Add support resources
    support_resources = analysis.get("support_resources", [])
    if support_resources:
        recommendations_text += f"\n\n📞 **Ресурсы поддержки:**"
        for resource in support_resources:
            recommendations_text += f"\n• {resource}"
    
    # Add prognosis
    prognosis = analysis.get("relationship_prognosis", "")
    if prognosis:
        recommendations_text += f"\n\n🔮 **Прогноз:** {prognosis}"
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к результатам", callback_data="back_to_results"),
        InlineKeyboardButton(text="📊 Детальный анализ", callback_data="detailed_analysis")
    )
    
    if urgency in ["HIGH", "CRITICAL"]:
        builder.row(
            InlineKeyboardButton(text="🚨 План безопасности", callback_data="safety_plan")
        )
    
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    await callback.message.edit_text(
        recommendations_text,
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "safety_plan", PartnerProfileStates.profile_complete)
@handle_errors
async def show_safety_plan(callback: CallbackQuery, state: FSMContext):
    """Show safety plan for high-risk situations"""
    data = await state.get_data()
    analysis = data.get("analysis_result", {})
    partner_name = data.get("partner_name", "партнер")
    
    if not analysis:
        await callback.answer("❌ Данные анализа недоступны")
        return
    
    urgency = analysis.get("urgency_level", "MEDIUM")
    safety_alerts = analysis.get("safety_alerts", [])
    
    safety_text = f"""🚨 **План безопасности**

⚠️ **Уровень угрозы:** {urgency}

🔍 **Выявленные проблемы:**"""
    
    # Add safety alerts
    if safety_alerts:
        for alert in safety_alerts:
            safety_text += f"\n• {alert}"
    else:
        safety_text += "\n• Общие рекомендации по безопасности"
    
    safety_text += f"""

🆘 **Экстренные контакты:**
• 112 - Служба экстренного реагирования
• 8-800-7000-600 - Всероссийская горячая линия
• 8-800-2000-122 - Детский телефон доверия

📋 **Если ситуация ухудшается:**
1. Обратитесь к близким за поддержкой
2. Зафиксируйте инциденты (дата, время, описание)
3. Обратитесь к специалисту-психологу
4. При угрозе физического насилия - звоните 112
5. Подготовьте план безопасного выхода

💼 **Документы для безопасности:**
• Паспорт и важные документы
• Банковские карты и наличные
• Лекарства и предметы первой необходимости
• Контакты близких людей

🏠 **Безопасные места:**
• Дом родственников или друзей
• Кризисные центры для женщин
• Социальные службы

⚠️ **Помните:** Ваша безопасность важнее отношений. Не стесняйтесь обращаться за помощью."""
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к результатам", callback_data="back_to_results"),
        InlineKeyboardButton(text="💡 Рекомендации", callback_data="recommendations")
    )
    builder.row(
        InlineKeyboardButton(text="📞 Горячие линии", url="tel:88007000600"),
        InlineKeyboardButton(text="🆘 Экстренные службы", url="tel:112")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    await callback.message.edit_text(
        safety_text,
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_results", PartnerProfileStates.profile_complete)
@handle_errors
async def back_to_results(callback: CallbackQuery, state: FSMContext):
    """Go back to analysis results"""
    await show_analysis_results(callback.message, state)
    await callback.answer()

@router.callback_query(F.data == "save_profile", PartnerProfileStates.profile_complete)
@handle_errors
async def save_profile(callback: CallbackQuery, state: FSMContext):
    """Save profile for future reference"""
    data = await state.get_data()
    partner_name = data.get("partner_name", "партнер")
    
    # TODO: Implement actual profile saving to database
    
    await callback.message.edit_text(
        f"💾 **Профиль сохранен**\n\n"
        f"Профиль партнера \"{partner_name}\" сохранен в ваш личный кабинет.\n\n"
        f"Вы можете вернуться к нему в любое время через "
        f"раздел \"📋 Мои профили\".\n\n"
        f"🔔 **Напоминание:** Рекомендуется повторить анализ через 3-6 месяцев "
        f"для отслеживания изменений в отношениях.",
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer("✅ Профиль сохранен")
    await state.clear()

@router.callback_query(F.data == "edit_answers", PartnerProfileStates.reviewing_answers)
@handle_errors
async def edit_answers(callback: CallbackQuery, state: FSMContext):
    """Edit questionnaire answers"""
    # Go back to first question to allow editing
    await state.set_state(PartnerProfileStates.narcissism_q1)
    
    await callback.message.edit_text(
        "✏️ **Редактирование ответов**\n\n"
        "Вы можете пройти анкету заново или изменить отдельные ответы.\n\n"
        "Начинаем с первого вопроса:",
        parse_mode="Markdown"
    )
    
    await show_question(callback.message, state, "narcissism_q1")
    await callback.answer()

@router.callback_query(F.data == "progress_info")
@handle_errors
async def show_progress_info(callback: CallbackQuery):
    """Show questionnaire progress information"""
    await callback.answer(
        "📊 Прогресс анкетирования\n\n"
        "Анкета состоит из 28 научно обоснованных вопросов в 6 блоках:\n"
        "🧠 Нарциссизм и грандиозность (6 вопросов)\n"
        "🎯 Контроль и манипуляции (6 вопросов)\n" 
        "🔄 Газлайтинг и искажение реальности (5 вопросов)\n"
        "💭 Эмоциональная регуляция (4 вопроса)\n"
        "💕 Интимность и принуждение (3 вопроса)\n"
        "👥 Социальное поведение (4 вопроса)",
        show_alert=True
    )

@router.callback_query(F.data == "my_profiles")
@handle_errors
async def my_profiles(callback: CallbackQuery):
    """Show user's profiles"""
    await callback.message.edit_text(
        "📋 **Мои профили**\n\n"
        "У вас пока нет сохранённых профилей.\n\n"
        "Создайте первый профиль партнера для получения "
        "персональных рекомендаций и анализа безопасности.",
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "profile_recommendations")
@handle_errors
async def profile_recommendations(callback: CallbackQuery):
    """Show profile recommendations"""
    await callback.message.edit_text(
        "🎯 **Рекомендации по отношениям**\n\n"
        "Для получения персональных рекомендаций "
        "необходимо создать профиль партнера.\n\n"
        "После анализа вы получите:\n"
        "• Оценку рисков в отношениях\n"
        "• Советы по безопасному общению\n" 
        "• Предупреждения о токсичных паттернах\n"
        "• План действий в критических ситуациях",
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(Command("profile"))
async def create_partner_profile(message: Message):
    """Handle partner profile creation command"""
    await message.answer(
        "👤 **Профиль партнера**\n\n"
        "Используйте команду /menu и выберите раздел "
        "\"👤 Профиль партнера\" для создания анализа.",
        parse_mode="Markdown"
    ) 

# ========== ENHANCED UI HANDLERS ==========

@router.callback_query(F.data == "prof_progress_visual")
@handle_errors
async def show_visual_progress(callback: CallbackQuery, state: FSMContext):
    """Show detailed visual progress"""
    data = await state.get_data()
    answers = data.get("answers", {})
    partner_name = data.get("partner_name", "партнер")
    
    # Calculate block progress
    block_progress = {}
    block_questions = {
        "narcissism": 6, "control": 6, "gaslighting": 5,
        "emotion": 4, "intimacy": 3, "social": 4
    }
    
    for block, total in block_questions.items():
        completed = sum(1 for q in answers.keys() if block in q)
        block_progress[f"{block}_completed"] = completed
        block_progress[f"{block}_total"] = total
    
    current_num = len(answers) + 1
    total_questions = 28
    
    progress_text = f"""📊 **Детальный прогресс профиля "{partner_name}"**

⏱️ **Время прохождения:** ~{len(answers) * 0.5:.1f} минут
🎯 **Завершено:** {len(answers)}/{total_questions} вопросов ({int(len(answers)/28*100)}%)

**Прогресс по блокам:**"""
    
    # Add detailed block progress
    block_names = {
        "narcissism": "🧠 Нарциссизм и грандиозность",
        "control": "🎯 Контроль и манипуляции",
        "gaslighting": "🔄 Газлайтинг и искажение реальности", 
        "emotion": "💭 Эмоциональная регуляция",
        "intimacy": "💕 Интимность и принуждение",
        "social": "👥 Социальное поведение"
    }
    
    for block, name in block_names.items():
        completed = block_progress.get(f"{block}_completed", 0)
        total = block_progress.get(f"{block}_total", 0)
        
        if total > 0:
            percent = int((completed / total) * 100)
            bar_length = 10
            filled = int((completed / total) * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            status = "✅" if completed == total else "⏳" if completed > 0 else "⏸️"
            progress_text += f"\n{status} {name}: {bar} {percent}%"
    
    await callback.message.edit_text(
        progress_text,
        reply_markup=profiler_progress_visual_kb(current_num, total_questions, block_progress),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "prof_back_to_question")
@handle_errors
async def back_to_current_question(callback: CallbackQuery, state: FSMContext):
    """Return to current question from progress view"""
    # Get current state and show appropriate question
    current_state = await state.get_state()
    if current_state:
        state_name = current_state.state.split(":")[-1]
        await show_question(callback.message, state, state_name)
    await callback.answer()


@router.callback_query(F.data == "prof_block_analysis")
@handle_errors
async def show_block_analysis_menu(callback: CallbackQuery, state: FSMContext):
    """Show block analysis navigation"""
    data = await state.get_data()
    analysis = data.get("analysis_result", {})
    
    if not analysis:
        await callback.answer("❌ Данные анализа недоступны")
        return
    
    block_scores = analysis.get("block_scores", {})
    
    analysis_text = f"""🔍 **Анализ по блокам**

Выберите блок для детального изучения:

**Легенда рисков:**
🟢 Низкий риск (0-3 балла)
🟡 Средний риск (4-6 баллов)  
🔴 Высокий риск (7-10 баллов)

**Текущие оценки:**"""
    
    for block, score in block_scores.items():
        risk_level = "🔴 Высокий" if score >= 7 else "🟡 Средний" if score >= 4 else "🟢 Низкий"
        block_names = {
            "narcissism": "🧠 Нарциссизм",
            "control": "🎯 Контроль",
            "gaslighting": "🔄 Газлайтинг",
            "emotion": "💭 Эмоции", 
            "intimacy": "💕 Интимность",
            "social": "👥 Социальное"
        }
        name = block_names.get(block, block)
        analysis_text += f"\n{name}: {score:.1f}/10 ({risk_level})"
    
    await callback.message.edit_text(
        analysis_text,
        reply_markup=profiler_block_analysis_kb(block_scores),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("prof_view_block_"))
@handle_errors
async def show_detailed_block_analysis(callback: CallbackQuery, state: FSMContext):
    """Show detailed analysis for specific block"""
    block_key = callback.data.replace("prof_view_block_", "")
    
    data = await state.get_data()
    analysis = data.get("analysis_result", {})
    partner_name = data.get("partner_name", "партнер")
    
    if not analysis:
        await callback.answer("❌ Данные анализа недоступны")
        return
    
    block_analysis = analysis.get("block_analysis", {})
    block_data = block_analysis.get(block_key, {})
    block_scores = analysis.get("block_scores", {})
    
    block_names = {
        "narcissism": "🧠 Нарциссизм и грандиозность",
        "control": "🎯 Контроль и манипуляции",
        "gaslighting": "🔄 Газлайтинг и искажение реальности",
        "emotion": "💭 Эмоциональная регуляция",
        "intimacy": "💕 Интимность и принуждение", 
        "social": "👥 Социальное поведение"
    }
    
    block_name = block_names.get(block_key, block_key)
    score = block_scores.get(block_key, 0)
    
    risk_emoji = "🔴" if score >= 7 else "🟡" if score >= 4 else "🟢"
    risk_level = "Высокий" if score >= 7 else "Средний" if score >= 4 else "Низкий"
    
    detailed_text = f"""📊 **Детальный анализ: {block_name}**

**Партнер:** {partner_name}
**Оценка:** {score:.1f}/10 {risk_emoji}
**Уровень риска:** {risk_level}

**🔍 Ключевые паттерны:**"""
    
    patterns = block_data.get("key_patterns", [])
    if patterns:
        for pattern in patterns[:5]:  # Show first 5 patterns
            detailed_text += f"\n• {pattern}"
    else:
        detailed_text += "\n• Недостаточно данных для анализа"
    
    evidence = block_data.get("evidence", "")
    if evidence:
        detailed_text += f"\n\n**📋 Обоснование:**\n{evidence[:300]}..."
    
    # Add specific recommendations for this block
    if score >= 7:
        detailed_text += f"\n\n⚠️ **КРИТИЧЕСКОЕ ПРЕДУПРЕЖДЕНИЕ:**\nВысокий уровень риска в этой области требует немедленного внимания."
    elif score >= 4:
        detailed_text += f"\n\n🟡 **ВНИМАНИЕ:**\nСредний уровень риска - рекомендуется мониторинг ситуации."
    
    await callback.message.edit_text(
        detailed_text,
        reply_markup=profiler_block_analysis_kb(block_scores, block_key),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "prof_emergency_help")
@handle_errors
async def show_emergency_help(callback: CallbackQuery, state: FSMContext):
    """Show emergency help contacts and resources"""
    emergency_text = """🚨 **ЭКСТРЕННАЯ ПОМОЩЬ**

**Если вы в опасности ПРЯМО СЕЙЧАС:**
• 📞 **112** - Служба экстренного реагирования
• 📞 **102** - Полиция России

**Горячие линии помощи (24/7):**
• 📞 **8-800-7000-600** - Национальная горячая линия
• 📞 **8-800-2000-122** - Детский телефон доверия
• 💬 **t.me/17000helpbot** - Чат поддержки

**Кризисные центры:**
• 🏠 Центр "Сестры" (Москва): 8-495-901-02-01
• 🏠 "АННА" (СПб): 8-812-671-30-00
• 🏠 "Насилию.Нет": nasiliu.net

**В критической ситуации:**
1. Обеспечьте безопасность
2. Звоните в службы экстренного реагирования
3. Обращайтесь к близким за поддержкой
4. Документируйте инциденты

**Помните:** Ваша безопасность - приоритет №1!"""

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📞 Позвонить 112", url="tel:112"),
        InlineKeyboardButton(text="☎️ Горячая линия", url="tel:88007000600")
    )
    builder.row(
        InlineKeyboardButton(text="🚨 План безопасности", callback_data="safety_plan"),
        InlineKeyboardButton(text="👥 Найти помощь", url="https://nasiliu.net")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ К результатам", callback_data="back_to_results")
    )
    
    await callback.message.edit_text(
        emergency_text,
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "prof_exit_confirm")
@handle_errors
async def confirm_exit(callback: CallbackQuery, state: FSMContext):
    """Confirm exit from questionnaire"""
    data = await state.get_data()
    answers_count = len(data.get("answers", {}))
    
    exit_text = f"""❓ **Вы действительно хотите выйти?**

📊 **Прогресс:** Отвечено на {answers_count}/28 вопросов
⚠️ **Внимание:** При выходе без сохранения прогресс будет потерян

**Варианты действий:**"""
    
    await callback.message.edit_text(
        exit_text,
        reply_markup=profiler_confirmation_kb("exit"),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "prof_save_progress")
@handle_errors
async def save_questionnaire_progress(callback: CallbackQuery, state: FSMContext):
    """Save current questionnaire progress"""
    data = await state.get_data()
    answers_count = len(data.get("answers", {}))
    partner_name = data.get("partner_name", "партнер")
    
    # TODO: Implement actual saving to database
    
    await callback.answer(
        f"✅ Прогресс сохранен!\n"
        f"📊 {answers_count}/28 ответов для профиля \"{partner_name}\"\n"
        f"Вы можете продолжить позже из меню \"Мои профили\"",
        show_alert=True
    )


@router.callback_query(F.data == "prof_save_and_exit")
@handle_errors
async def save_and_exit_questionnaire(callback: CallbackQuery, state: FSMContext):
    """Save progress and exit to main menu"""
    data = await state.get_data()
    answers_count = len(data.get("answers", {}))
    partner_name = data.get("partner_name", "партнер")
    
    # TODO: Implement actual saving
    
    await callback.message.edit_text(
        f"💾 **Прогресс сохранен**\n\n"
        f"Профиль \"{partner_name}\" сохранен с {answers_count}/28 ответами.\n\n"
        f"Вы можете продолжить анкету позже через раздел \"📋 Мои профили\".",
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "prof_exit_no_save")
@handle_errors
async def exit_without_saving(callback: CallbackQuery, state: FSMContext):
    """Exit without saving progress"""
    await callback.message.edit_text(
        "❌ **Прогресс не сохранен**\n\n"
        "Вы вышли из анкеты без сохранения. "
        "Для создания профиля партнера начните анкету заново.",
        reply_markup=back_to_main_kb(),
        parse_mode="Markdown"
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "prof_continue")
@handle_errors
async def continue_questionnaire(callback: CallbackQuery, state: FSMContext):
    """Continue with questionnaire"""
    # Return to current question
    await back_to_current_question(callback, state)


@router.callback_query(F.data.startswith("prof_skip_"))
@handle_errors
async def skip_question(callback: CallbackQuery, state: FSMContext):
    """Skip current question (for non-critical questions only)"""
    question_state = callback.data.replace("prof_skip_", "")
    
    # Get next question
    next_state = get_next_question_state(question_state)
    
    if next_state == "reviewing_answers":
        await show_review(callback.message, state)
    else:
        await state.set_state(getattr(PartnerProfileStates, next_state))
        await show_question(callback.message, state, next_state)
    
    await callback.answer("⏭️ Вопрос пропущен")


@router.callback_query(F.data.startswith("prof_block_info_"))
@handle_errors
async def show_block_info(callback: CallbackQuery):
    """Show information about current block"""
    question_state = callback.data.replace("prof_block_info_", "")
    block_name = get_block_by_question(question_state)
    
    block_descriptions = {
        "Нарциссизм и грандиозность": """🧠 **Нарциссизм и грандиозность**

Этот блок оценивает признаки нарциссического расстройства личности:
• Завышенная самооценка и чувство превосходства
• Потребность в постоянном восхищении
• Отсутствие эмпатии к другим
• Неадекватная реакция на критику
• Эксплуатация других для достижения целей

*Основано на критериях DSM-5 и исследованиях Dark Triad*""",
        
        "Контроль и манипуляции": """🎯 **Контроль и манипуляции**

Оценка попыток контролировать поведение партнера:
• Контроль времени, социальных связей, финансов
• Изоляция от друзей и семьи
• Эмоциональный шантаж и принуждение
• Нарушение личных границ
• Использование угроз и запугивания

*На основе Duluth Model и исследований абьюзивных отношений*""",
        
        "Газлайтинг и искажение реальности": """🔄 **Газлайтинг и искажение реальности**

Анализ попыток искажения восприятия реальности:
• Отрицание произошедших событий
• Обесценивание чувств и переживаний
• Перекладывание вины на жертву
• Использование личной информации против партнера
• Создание двойных стандартов

*Основано на концепции газлайтинга и когнитивных искажений*""",
        
        "Эмоциональная регуляция": """💭 **Эмоциональная регуляция**

Оценка способности управлять эмоциями:
• Контроль гнева и агрессии
• Эмоциональная стабильность
• Способность к прощению
• Стрессоустойчивость
• Эмоциональная поддержка партнера

*На основе теории эмоциональной регуляции и attachment theory*""",
        
        "Интимность и принуждение": """💕 **Интимность и принуждение**

Анализ поведения в интимной сфере:
• Уважение к согласию и границам
• Использование интимности для контроля
• Принуждение и сексуальная агрессия
• Контроль внешности партнера
• Ревность к прошлым отношениям

*Основано на исследованиях сексуального принуждения*""",
        
        "Социальное поведение": """👥 **Социальное поведение**

Оценка социального функционирования:
• Последовательность поведения в разных ситуациях
• Отношение к людям разного статуса
• Способность к дружеским отношениям
• Профессиональные взаимоотношения
• Использование "масок" и социальной мимикрии

*На основе теории социальной психологии и макиавеллизма*"""
    }
    
    description = block_descriptions.get(block_name, f"Информация о блоке '{block_name}' недоступна.")
    
    await callback.answer(description, show_alert=True)


@router.callback_query(F.data == "prof_my_profiles")
@handle_errors
async def show_my_profiles(callback: CallbackQuery):
    """Show user's saved profiles"""
    # TODO: Get actual profiles count from database
    profiles_count = 0
    
    await callback.message.edit_text(
        "📋 **Мои профили партнеров**\n\n" + 
        ("У вас пока нет сохранённых профилей.\n\n"
         "Создайте первый профиль для получения "
         "персональных рекомендаций по безопасности отношений." if profiles_count == 0 
         else f"У вас {profiles_count} сохранённых профилей."),
        reply_markup=profiler_my_profiles_kb(profiles_count),
        parse_mode="Markdown"
    )
    await callback.answer() 