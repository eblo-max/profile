"""Profiler handler for partner analysis"""

import asyncio
from typing import Dict, Any
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from loguru import logger

from app.bot.states import ProfilerStates, PartnerProfileStates, FreeFormProfilerStates
from app.bot.keyboards.inline import profiler_menu_kb, get_profiler_keyboard, get_profiler_navigation_keyboard, get_profiler_question_keyboard
from app.services.ai_service import AIService
from app.services.html_pdf_service import HTMLPDFService
from app.services.user_service import UserService
from app.services.profile_service import ProfileService
from app.utils.exceptions import ServiceError
from app.utils.enums import AnalysisType
from app.prompts.profiler_full_questions import (
    get_all_questions, get_free_form_questions, is_free_form_question,
    calculate_weighted_scores, get_urgency_level, get_safety_alerts
)

router = Router()


@router.callback_query(F.data == "profiler_menu")
async def show_profiler_menu(callback: CallbackQuery, state: FSMContext, profile_service: ProfileService):
    """Show profiler main menu"""
    try:
        # Get user from database by telegram_id
        telegram_id = callback.from_user.id
        
        # Get user service from middleware or create session
        from app.core.database import get_session
        from app.services.user_service import UserService
        
        async with get_session() as session:
            user_service = UserService(session)
            user = await user_service.get_user_by_telegram_id(telegram_id)
            
            if not user:
                await callback.message.edit_text(
                    "❌ Пользователь не найден. Используйте /start для регистрации.",
                    reply_markup=get_profiler_keyboard()
                )
                return
        
        user_id = user.id  # Internal database ID
        
        # Get user's profile count
        profile_count = await profile_service._get_user_profile_count(user_id)
        
        # Create menu text
        menu_text = f"""🧠 <b>ПСИХОЛОГИЧЕСКИЙ ПРОФАЙЛЕР ПАРТНЕРА</b>

👤 <b>Ваши профили:</b> {profile_count}

<b>Научные методики 2025:</b>
• Разработка в кооперации с психологами и психиатрами
• Применение техник DSM-5 и ICD-11
• Анализ Dark Triad (нарциссизм, макиавеллизм, психопатия)
• Методы клинической психологии
• Техники поведенческого анализа
• Система оценки манипулятивного поведения

<b>Что вы хотите сделать?</b>

<b>Новый профиль</b> - профессиональный анализ партнера
<b>Мои профили</b> - просмотреть сохраненные профили
<b>Рекомендации</b> - получить советы по отношениям

<i>Время анализа: 3-5 минут</i>
<i>Максимальная точность и детализация</i>"""
        
        # Show menu
        await callback.message.edit_text(
            menu_text,
            parse_mode="HTML",
            reply_markup=get_profiler_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in show_profiler_menu: {e}")
        await callback.answer("❌ Произошла ошибка")


@router.callback_query(F.data == "create_profile")
async def create_new_profile(callback: CallbackQuery, state: FSMContext):
    """Create new profile - show introduction and start data collection"""
    try:
        await callback.message.edit_text(
            "🧠 <b>ПСИХОЛОГИЧЕСКИЙ АНАЛИЗ ПАРТНЕРА</b>\n\n"
            "<b>Научная система 2025:</b>\n"
            "• Разработка в кооперации с психологами и психиатрами\n"
            "• Применение методик DSM-5 и ICD-11\n"
            "• Анализ Dark Triad (нарциссизм, макиавеллизм, психопатия)\n"
            "• Техники клинической психологии\n"
            "• Методы поведенческого анализа\n\n"
            "<b>Что будет происходить:</b>\n"
            "• Расскажите о партнере (2 минуты)\n"
            "• Ответите на 28 вопросов в свободной форме (15-20 минут)\n"
            "• Получите детальный анализ (3-5 минут)\n"
            "• Узнаете детальные риски и рекомендации\n\n"
            "<b>Общее время:</b> 20-27 минут\n"
            "<b>Конфиденциальность:</b> Все данные защищены\n"
            "<b>Качество:</b> Максимальная точность анализа\n\n"
            "Готовы к профессиональному анализу?",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🚀 Начать анализ", callback_data="start_partner_info")],
                [InlineKeyboardButton(text="🔙 Назад", callback_data="profiler_menu")]
            ])
        )
    except Exception as e:
        logger.error(f"Error in create_new_profile: {e}")
        await callback.answer("❌ Произошла ошибка")


@router.callback_query(F.data == "start_partner_info")
async def start_partner_info_collection(callback: CallbackQuery, state: FSMContext):
    """Start collecting partner information"""
    try:
        await state.set_state(PartnerProfileStates.waiting_for_name)
        # Автоматически устанавливаем флаг свободной формы
        await state.update_data(is_free_form=True)
        await callback.message.edit_text(
            "👤 <b>Информация о партнере</b>\n\n"
            "Как зовут вашего партнера?\n\n"
            "💡 <i>Можете использовать псевдоним или инициалы для конфиденциальности</i>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="create_profile")]
            ])
        )
    except Exception as e:
        logger.error(f"Error in start_partner_info_collection: {e}")
        await callback.answer("❌ Произошла ошибка")


@router.message(PartnerProfileStates.waiting_for_name)
async def process_partner_name(message: Message, state: FSMContext):
    """Process partner name input"""
    try:
        partner_name = message.text.strip()
        
        if not partner_name or len(partner_name) < 1:
            await message.answer(
                "❌ <b>Имя не может быть пустым</b>\n\n"
                "Пожалуйста, введите имя партнера:",
                parse_mode="HTML"
            )
            return
        
        if len(partner_name) > 100:
            await message.answer(
                "❌ <b>Имя слишком длинное</b>\n\n"
                "Пожалуйста, введите имя до 100 символов:",
                parse_mode="HTML"
            )
            return
        
        await state.update_data(partner_name=partner_name)
        await state.set_state(PartnerProfileStates.waiting_for_description)
        
        await message.answer(
            f"✅ <b>Имя партнера:</b> {partner_name}\n\n"
            "📝 <b>Опишите вашего партнера</b>\n\n"
            "Расскажите о нем в свободной форме:\n"
            "• Как вы познакомились?\n"
            "• Какой он человек?\n"
            "• Что вам в нем нравится?\n"
            "• Есть ли что-то, что вас беспокоит?\n\n"
            "💬 <i>Пишите как хотите, без ограничений</i>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_name")]
            ])
        )
    except Exception as e:
        logger.error(f"Error in process_partner_name: {e}")
        await message.answer("❌ Произошла ошибка")


@router.message(PartnerProfileStates.waiting_for_description)
async def process_partner_description(message: Message, state: FSMContext):
    """Process partner description input"""
    try:
        description = message.text.strip()
        
        if not description or len(description) < 10:
            await message.answer(
                "❌ <b>Описание слишком короткое</b>\n\n"
                "Пожалуйста, расскажите больше о партнере (минимум 10 символов):",
                parse_mode="HTML"
            )
            return
        
        if len(description) > 2000:
            await message.answer(
                "❌ <b>Описание слишком длинное</b>\n\n"
                "Пожалуйста, сократите описание до 2000 символов:",
                parse_mode="HTML"
            )
            return
        
        await state.update_data(partner_description=description)
        await state.set_state(PartnerProfileStates.waiting_for_basic_info)
        
        await message.answer(
            "✅ <b>Описание сохранено</b>\n\n"
            "📊 <b>Базовые данные партнера</b>\n\n"
            "Укажите дополнительную информацию (одним сообщением):\n"
            "• Возраст (примерно)\n"
            "• Род деятельности/работа\n"
            "• Семейное положение\n"
            "• Сколько времени вы знакомы\n\n"
            "📝 <b>Пример:</b>\n"
            "<i>30 лет, программист, холост, знакомы 8 месяцев</i>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_description")]
            ])
        )
    except Exception as e:
        logger.error(f"Error in process_partner_description: {e}")
        await message.answer("❌ Произошла ошибка")


@router.message(PartnerProfileStates.waiting_for_basic_info)
async def process_partner_basic_info(message: Message, state: FSMContext):
    """Process partner basic info and proceed to questions"""
    try:
        basic_info = message.text.strip()
        
        if not basic_info or len(basic_info) < 5:
            await message.answer(
                "❌ <b>Информация слишком короткая</b>\n\n"
                "Пожалуйста, укажите хотя бы базовые данные:",
                parse_mode="HTML"
            )
            return
        
        if len(basic_info) > 500:
            await message.answer(
                "❌ <b>Информация слишком длинная</b>\n\n"
                "Пожалуйста, сократите до 500 символов:",
                parse_mode="HTML"
            )
            return
        
        await state.update_data(partner_basic_info=basic_info)
        
        # Get saved data
        data = await state.get_data()
        partner_name = data.get('partner_name', 'Партнер')
        
        # Check if this is free form version
        data = await state.get_data()
        is_free_form = data.get('is_free_form', True)  # По умолчанию теперь свободная форма
        
        await message.answer(
            f"✅ <b>Информация о {partner_name} сохранена</b>\n\n"
            "🎯 <b>Переходим к психологическому опросу</b>\n\n"
            "💫 <b>Следующий этап:</b> 28 вопросов в свободной форме\n\n"
            "🔬 <b>Эти данные будут обработаны:</b>\n"
            "• Научными методиками анализа текста\n"
            "• Максимально детальным профайлингом\n"
            "• Персонализированным подходом\n\n"
            "⏱️ <b>Время опроса:</b> 15-20 минут\n"
            "🎯 <b>Точность анализа:</b> максимальная\n"
            "🔒 <b>Конфиденциально:</b> Никто не увидит ваши ответы\n\n"
            "Отвечайте максимально подробно - это критично для качества анализа!",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🚀 Начать опрос", callback_data="start_free_form_questions")],
                [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_basic_info")]
            ])
        )
    except Exception as e:
        logger.error(f"Error in process_partner_basic_info: {e}")
        await message.answer("❌ Произошла ошибка")


@router.callback_query(F.data == "back_to_name")
async def back_to_name_input(callback: CallbackQuery, state: FSMContext):
    """Go back to name input"""
    try:
        await state.set_state(PartnerProfileStates.waiting_for_name)
        await callback.message.edit_text(
            "👤 <b>Информация о партнере</b>\n\n"
            "Как зовут вашего партнера?\n\n"
            "💡 <i>Можете использовать псевдоним или инициалы для конфиденциальности</i>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="create_profile")]
            ])
        )
    except Exception as e:
        logger.error(f"Error in back_to_name_input: {e}")
        await callback.answer("❌ Произошла ошибка")


@router.callback_query(F.data == "back_to_description")
async def back_to_description_input(callback: CallbackQuery, state: FSMContext):
    """Go back to description input"""
    try:
        data = await state.get_data()
        partner_name = data.get('partner_name', 'вашего партнера')
        
        await state.set_state(PartnerProfileStates.waiting_for_description)
        await callback.message.edit_text(
            f"✅ <b>Имя партнера:</b> {partner_name}\n\n"
            "📝 <b>Опишите вашего партнера</b>\n\n"
            "Расскажите о нем в свободной форме:\n"
            "• Как вы познакомились?\n"
            "• Какой он человек?\n"
            "• Что вам в нем нравится?\n"
            "• Есть ли что-то, что вас беспокоит?\n\n"
            "💬 <i>Пишите как хотите, без ограничений</i>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_name")]
            ])
        )
    except Exception as e:
        logger.error(f"Error in back_to_description_input: {e}")
        await callback.answer("❌ Произошла ошибка")


@router.callback_query(F.data == "back_to_basic_info")
async def back_to_basic_info_input(callback: CallbackQuery, state: FSMContext):
    """Go back to basic info input"""
    try:
        await state.set_state(PartnerProfileStates.waiting_for_basic_info)
        
        data = await state.get_data()
        partner_name = data.get('partner_name', 'партнер')
        
        await callback.message.edit_text(
            f"📝 <b>Базовая информация о {partner_name}</b>\n\n"
            "Расскажите о вашем партнере в свободной форме:\n"
            "• Как давно вы вместе?\n"
            "• Какие у вас отношения?\n"
            "• Что вас беспокоит или радует?\n"
            "• Любые детали, которые считаете важными\n\n"
            "💬 <i>Пишите всё, что считаете нужным</i>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_description")]
            ])
        )
    except Exception as e:
        logger.error(f"Error in back_to_basic_info_input: {e}")
        await callback.answer("❌ Произошла ошибка")


# Универсальный обработчик для всех текстовых ответов
async def process_text_answer(message: Message, state: FSMContext, question_id: str, current_question_num: int, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    """Универсальный обработчик текстовых ответов"""
    try:
        answer_text = message.text.strip()
        
        # Get question data
        data = await state.get_data()
        free_form_questions = data.get('free_form_questions', {})
        question_order = data.get('question_order', [])
        question = free_form_questions.get(question_id, {})
        min_length = question.get('min_length', 50)
        
        # Check if analysis is already running
        if data.get('analysis_running', False):
            logger.warning(f"Analysis already running for user {message.from_user.id}, ignoring duplicate")
            return
        
        # Validate answer length
        if len(answer_text) < min_length:
            await message.answer(
                f"❌ <b>Ответ слишком короткий</b>\n\n"
                f"Пожалуйста, напишите более подробный ответ (минимум {min_length} символов).\n\n"
                f"💡 <b>Подсказки:</b>\n"
                + "\n".join([f"• {hint}" for hint in question.get('prompt_hints', [])]),
                parse_mode="HTML"
            )
            return
        
        # Save answer
        text_answers = data.get('text_answers', {})
        text_answers[question_id] = answer_text
        
        # Check if this was the last question (current_question_num is 1-based, so 28 is the last)
        total_questions = len(question_order)
        is_last_question = current_question_num == total_questions
        
        if is_last_question:
            # All questions answered - start analysis
            await state.update_data(text_answers=text_answers, analysis_running=True)
            await start_analysis(message, state, ai_service, html_pdf_service, user_service, profile_service, message.from_user.id)
        else:
            # Move to next question
            next_question_num = current_question_num + 1
            next_question_id = question_order[current_question_num]  # current_question_num is already the next index (0-based)
            next_question = free_form_questions.get(next_question_id, {})
            
            # Update state
            await state.update_data(
                text_answers=text_answers,
                current_question=current_question_num
            )
            
            # Set next state
            state_mapping = {
                "narcissism_q1": FreeFormProfilerStates.narcissism_q1_text,
                "narcissism_q2": FreeFormProfilerStates.narcissism_q2_text,
                "narcissism_q3": FreeFormProfilerStates.narcissism_q3_text,
                "narcissism_q4": FreeFormProfilerStates.narcissism_q4_text,
                "narcissism_q5": FreeFormProfilerStates.narcissism_q5_text,
                "narcissism_q6": FreeFormProfilerStates.narcissism_q6_text,
                "control_q1": FreeFormProfilerStates.control_q1_text,
                "control_q2": FreeFormProfilerStates.control_q2_text,
                "control_q3": FreeFormProfilerStates.control_q3_text,
                "control_q4": FreeFormProfilerStates.control_q4_text,
                "control_q5": FreeFormProfilerStates.control_q5_text,
                "control_q6": FreeFormProfilerStates.control_q6_text,
                "gaslighting_q1": FreeFormProfilerStates.gaslighting_q1_text,
                "gaslighting_q2": FreeFormProfilerStates.gaslighting_q2_text,
                "gaslighting_q3": FreeFormProfilerStates.gaslighting_q3_text,
                "gaslighting_q4": FreeFormProfilerStates.gaslighting_q4_text,
                "gaslighting_q5": FreeFormProfilerStates.gaslighting_q5_text,
                "emotion_q1": FreeFormProfilerStates.emotion_q1_text,
                "emotion_q2": FreeFormProfilerStates.emotion_q2_text,
                "emotion_q3": FreeFormProfilerStates.emotion_q3_text,
                "emotion_q4": FreeFormProfilerStates.emotion_q4_text,
                "intimacy_q1": FreeFormProfilerStates.intimacy_q1_text,
                "intimacy_q2": FreeFormProfilerStates.intimacy_q2_text,
                "intimacy_q3": FreeFormProfilerStates.intimacy_q3_text,
                "social_q1": FreeFormProfilerStates.social_q1_text,
                "social_q2": FreeFormProfilerStates.social_q2_text,
                "social_q3": FreeFormProfilerStates.social_q3_text,
                "social_q4": FreeFormProfilerStates.social_q4_text,
            }
            
            next_state = state_mapping.get(next_question_id)
            if next_state:
                await state.set_state(next_state)
            
            partner_name = data.get('partner_name', 'партнера')
            
            await message.answer(
                f"✅ <b>Ответ сохранен</b>\n\n"
                f"🎯 <b>Вопрос {next_question_num} из {total_questions}</b> (Свободная форма)\n\n"
            f"📝 <b>О {partner_name}:</b>\n\n"
                f"❓ <b>{next_question['text']}</b>\n\n"
                f"💭 <i>{next_question['context']}</i>\n\n"
                f"🔍 <b>Подсказки для ответа:</b>\n"
                + "\n".join([f"• {hint}" for hint in next_question['prompt_hints']]) + "\n\n"
                f"💡 <b>Пример ответа:</b>\n"
                f"<i>{next_question['example']}</i>\n\n"
                f"✏️ <b>Напишите ваш ответ:</b>\n"
                f"<i>Минимум {next_question['min_length']} символов</i>",
                parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error in process_text_answer: {e}")
        await message.answer("❌ Произошла ошибка")

# Обработчики для всех 28 вопросов
@router.message(FreeFormProfilerStates.narcissism_q1_text)
async def process_narcissism_q1_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "narcissism_q1", 1, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.narcissism_q2_text)
async def process_narcissism_q2_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "narcissism_q2", 2, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.narcissism_q3_text)
async def process_narcissism_q3_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "narcissism_q3", 3, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.narcissism_q4_text)
async def process_narcissism_q4_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "narcissism_q4", 4, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.narcissism_q5_text)
async def process_narcissism_q5_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "narcissism_q5", 5, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.narcissism_q6_text)
async def process_narcissism_q6_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "narcissism_q6", 6, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.control_q1_text)
async def process_control_q1_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "control_q1", 7, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.control_q2_text)
async def process_control_q2_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "control_q2", 8, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.control_q3_text)
async def process_control_q3_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "control_q3", 9, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.control_q4_text)
async def process_control_q4_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "control_q4", 10, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.control_q5_text)
async def process_control_q5_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "control_q5", 11, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.control_q6_text)
async def process_control_q6_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "control_q6", 12, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.gaslighting_q1_text)
async def process_gaslighting_q1_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "gaslighting_q1", 13, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.gaslighting_q2_text)
async def process_gaslighting_q2_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "gaslighting_q2", 14, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.gaslighting_q3_text)
async def process_gaslighting_q3_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "gaslighting_q3", 15, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.gaslighting_q4_text)
async def process_gaslighting_q4_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "gaslighting_q4", 16, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.gaslighting_q5_text)
async def process_gaslighting_q5_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "gaslighting_q5", 17, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.emotion_q1_text)
async def process_emotion_q1_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "emotion_q1", 18, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.emotion_q2_text)
async def process_emotion_q2_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "emotion_q2", 19, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.emotion_q3_text)
async def process_emotion_q3_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "emotion_q3", 20, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.emotion_q4_text)
async def process_emotion_q4_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "emotion_q4", 21, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.intimacy_q1_text)
async def process_intimacy_q1_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "intimacy_q1", 22, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.intimacy_q2_text)
async def process_intimacy_q2_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "intimacy_q2", 23, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.intimacy_q3_text)
async def process_intimacy_q3_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "intimacy_q3", 24, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.social_q1_text)
async def process_social_q1_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "social_q1", 25, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.social_q2_text)
async def process_social_q2_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "social_q2", 26, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.social_q3_text)
async def process_social_q3_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "social_q3", 27, ai_service, html_pdf_service, user_service, profile_service)

@router.message(FreeFormProfilerStates.social_q4_text)
async def process_social_q4_text(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    await process_text_answer(message, state, "social_q4", 28, ai_service, html_pdf_service, user_service, profile_service)


@router.callback_query(F.data == "my_profiles")
async def show_my_profiles(callback: CallbackQuery, state: FSMContext, profile_service: ProfileService):
    """Show user's existing profiles"""
    try:
        # Get user from database by telegram_id
        telegram_id = callback.from_user.id
        
        # Get user service from middleware or create session
        from app.core.database import get_session
        from app.services.user_service import UserService
        
        async with get_session() as session:
            user_service = UserService(session)
            user = await user_service.get_user_by_telegram_id(telegram_id)
            
            if not user:
                await callback.message.edit_text(
                    "❌ Пользователь не найден. Используйте /start для регистрации.",
                    reply_markup=get_profiler_keyboard()
                )
                return
        
        user_id = user.id  # Internal database ID
        
        # Get user's profiles
        profiles = await profile_service.get_user_profiles(user_id, limit=10)
        
        if not profiles:
            await callback.message.edit_text(
                "📂 <b>Мои профили</b>\n\n"
                "У вас пока нет сохраненных профилей партнеров.\n\n"
                "Создайте новый профиль, чтобы получить детальный анализ вашего партнера.",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🆕 Создать профиль", callback_data="create_profile")],
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="profiler_menu")]
                ])
            )
            return
        
        # Build profiles list
        profiles_text = "📂 <b>Мои профили</b>\n\n"
        keyboard = []
        
        for i, profile in enumerate(profiles, 1):
            # Get risk info
            risk_emoji = "🔴" if profile.manipulation_risk >= 7 else "🟡" if profile.manipulation_risk >= 4 else "🟢"
            partner_name = profile.partner_name or f"Партнер #{profile.id}"
            
            profiles_text += f"{i}. {risk_emoji} <b>{partner_name}</b>\n"
            profiles_text += f"   Риск: {profile.manipulation_risk:.1f}/10\n"
            profiles_text += f"   Создан: {profile.created_at.strftime('%d.%m.%Y')}\n\n"
            
            # Add profile button
            keyboard.append([InlineKeyboardButton(
                text=f"📋 {partner_name}", 
                callback_data=f"view_profile_{profile.id}"
            )])
        
        # Add control buttons
        keyboard.append([
            InlineKeyboardButton(text="🆕 Новый профиль", callback_data="create_profile"),
            InlineKeyboardButton(text="🔄 Обновить", callback_data="my_profiles")
        ])
        keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="profiler_menu")])
        
        await callback.message.edit_text(
            profiles_text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        
    except Exception as e:
        logger.error(f"Error in show_my_profiles: {e}")
        await callback.answer("❌ Произошла ошибка при загрузке профилей")


@router.callback_query(F.data == "profile_recommendations")
async def show_profile_recommendations(callback: CallbackQuery, state: FSMContext, profile_service: ProfileService):
    """Show profile-based recommendations"""
    try:
        # Get user from database by telegram_id
        telegram_id = callback.from_user.id
        
        # Get user service from middleware or create session
        from app.core.database import get_session
        from app.services.user_service import UserService
        
        async with get_session() as session:
            user_service = UserService(session)
            user = await user_service.get_user_by_telegram_id(telegram_id)
            
            if not user:
                await callback.message.edit_text(
                    "❌ Пользователь не найден. Используйте /start для регистрации.",
                    reply_markup=get_profiler_keyboard()
                )
                return
        
        user_id = user.id  # Internal database ID
        
        # Get user's profiles for analysis
        profiles = await profile_service.get_user_profiles(user_id, limit=10)
        
        if not profiles:
            await callback.message.edit_text(
                "💡 <b>Рекомендации</b>\n\n"
                "У вас пока нет профилей для анализа.\n\n"
                "Создайте профиль партнера, чтобы получить персональные рекомендации.",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🆕 Создать профиль", callback_data="create_profile")],
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="profiler_menu")]
                ])
            )
            return
        
        # Analyze profiles and create recommendations
        recommendations_text = "💡 <b>Рекомендации</b>\n\n"
        
        # Count risk levels
        high_risk = len([p for p in profiles if p.manipulation_risk >= 7])
        medium_risk = len([p for p in profiles if 4 <= p.manipulation_risk < 7])
        low_risk = len([p for p in profiles if p.manipulation_risk < 4])
        
        # General recommendations
        if high_risk > 0:
            recommendations_text += "🔴 <b>ВНИМАНИЕ:</b> Обнаружены высокорисковые профили\n"
            recommendations_text += "• Рекомендуется консультация с психологом\n"
            recommendations_text += "• Изучите техники защиты от манипуляций\n"
            recommendations_text += "• Установите четкие границы в отношениях\n\n"
        
        if medium_risk > 0:
            recommendations_text += "🟡 <b>Средний риск:</b> Требуется внимание\n"
            recommendations_text += "• Изучите красные флаги в отношениях\n"
            recommendations_text += "• Развивайте эмоциональный интеллект\n"
            recommendations_text += "• Обратите внимание на паттерны поведения\n\n"
        
        if low_risk > 0:
            recommendations_text += "🟢 <b>Низкий риск:</b> Хорошие показатели\n"
            recommendations_text += "• Продолжайте развивать здоровые отношения\n"
            recommendations_text += "• Изучайте психологию совместимости\n"
            recommendations_text += "• Делитесь опытом с другими\n\n"
        
        # Specific recommendations based on latest profile
        latest_profile = profiles[0]
        if latest_profile.red_flags:
            recommendations_text += "🚨 <b>Основные красные флаги:</b>\n"
            for flag in latest_profile.red_flags[:3]:  # Top 3
                recommendations_text += f"• {flag}\n"
            recommendations_text += "\n"
        
        if latest_profile.relationship_advice:
            recommendations_text += "📋 <b>Персональные советы:</b>\n"
            advice_lines = latest_profile.relationship_advice.split('\n')
            for line in advice_lines[:3]:  # Top 3
                if line.strip():
                    recommendations_text += f"• {line.strip()}\n"
            recommendations_text += "\n"
        
        # Add profile-specific buttons
        keyboard = []
        for profile in profiles[:3]:  # Show top 3 profiles
            partner_name = profile.partner_name or f"Партнер #{profile.id}"
            risk_emoji = "🔴" if profile.manipulation_risk >= 7 else "🟡" if profile.manipulation_risk >= 4 else "🟢"
            keyboard.append([InlineKeyboardButton(
                text=f"{risk_emoji} Советы для {partner_name}",
                callback_data=f"recommendations_{profile.id}"
            )])
        
        keyboard.append([
            InlineKeyboardButton(text="📂 Мои профили", callback_data="my_profiles"),
            InlineKeyboardButton(text="🔄 Обновить", callback_data="profile_recommendations")
        ])
        keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="profiler_menu")])
        
        await callback.message.edit_text(
            recommendations_text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        
    except Exception as e:
        logger.error(f"Error in show_profile_recommendations: {e}")
        await callback.answer("❌ Произошла ошибка при загрузке рекомендаций")


def get_block_emoji(block: str) -> str:
    """Get emoji for block"""
    block_emoji = {
        "narcissism": "🧠",
        "control": "🎯", 
        "gaslighting": "🔄",
        "emotion": "💭",
        "intimacy": "💕",
        "social": "👥"
    }
    return block_emoji.get(block, "❓")


async def start_analysis(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService, telegram_id: int):
    """Start AI analysis of free form answers"""
    try:
        # Get user from database
        from app.core.database import get_session
        from app.services.user_service import UserService
        from app.services.profile_service import ProfileService
        
        async with get_session() as session:
            local_user_service = UserService(session)
            local_profile_service = ProfileService(session)
            
            user = await local_user_service.get_user_by_telegram_id(telegram_id)
            
            if not user:
                logger.error(f"User not found in database for telegram_id: {telegram_id}")
                await message.answer("❌ Пользователь не найден. Используйте /start для регистрации.")
                return
            
            user_id = user.id  # Internal database ID
        
        data = await state.get_data()
        text_answers = data.get('text_answers', {})
        
        # Get partner info from state
        partner_name = data.get('partner_name', 'Партнер')
        partner_description = data.get('partner_description', '')
        partner_basic_info = data.get('partner_basic_info', '')
        
        # Send analysis start message
        analysis_msg = await message.answer(
            f"🧠 <b>ПСИХОЛОГИЧЕСКИЙ АНАЛИЗ: {partner_name}</b>\n\n"
            "<b>Этап 1/5:</b> Параллельный анализ экспертных методик\n"
            "<b>Этап 2/5:</b> Кросс-валидация результатов\n"
            "<b>Этап 3/5:</b> Формирование экспертного консенсуса\n"
            "<b>Этап 4/5:</b> Создание живых сценариев\n"
            "<b>Этап 5/5:</b> Финальная интеграция\n\n"
            "<b>Применяются:</b> Методики психологов и психиатров\n"
            "<b>Ожидаемое время:</b> 3-5 минут",
            parse_mode="HTML"
        )
        
        # Convert text answers to format expected by AI service
        formatted_answers = []
        free_form_questions = data.get('free_form_questions', {})
        
        for question_id, answer_text in text_answers.items():
            question = free_form_questions.get(question_id, {})
                formatted_answers.append({
                    'question_id': question_id,
                    'question': question.get('text', ''),
                'answer': answer_text,
                'block': question.get('block', 'unknown')
            })
        
        # Perform AI analysis with enhanced prompt for free form
        try:
            analysis_result = await ai_service.profile_partner_free_form(
                text_answers=formatted_answers,
                user_id=telegram_id,
                partner_name=partner_name,
                partner_description=partner_description,
                partner_basic_info=partner_basic_info
            )
            
            # Update progress
            await analysis_msg.edit_text(
                f"🧠 <b>ПСИХОЛОГИЧЕСКИЙ АНАЛИЗ: {partner_name}</b>\n\n"
                "✅ <b>Этап 1/5:</b> Параллельный анализ экспертных методик\n"
                "✅ <b>Этап 2/5:</b> Кросс-валидация результатов\n"
                "✅ <b>Этап 3/5:</b> Формирование экспертного консенсуса\n"
                "✅ <b>Этап 4/5:</b> Создание живых сценариев\n"
                "✅ <b>Этап 5/5:</b> Финальная интеграция\n\n"
                "🎯 <b>Психологический анализ завершен!</b>\n"
                "📋 Генерирую расширенный PDF отчет...\n\n"
                "<i>Почти готово!</i>",
                parse_mode="HTML"
            )
            
            # Generate PDF report
            pdf_bytes = await html_pdf_service.generate_partner_report_html(
                analysis_result,
                telegram_id,
                partner_name
            )
            
            # Save analysis to database
            try:
                    await local_user_service.save_analysis(
                    user_id=user_id,
                    analysis_type=AnalysisType.PARTNER_PROFILE,
                    analysis_data=analysis_result,
                    questions=formatted_answers
                )
            except Exception as e:
                logger.warning(f"Failed to save analysis to DB: {e}")
            
            # Save partner profile to database
            try:
                    await local_profile_service.create_profile_from_profiler(
                    user_id=user_id,
                    partner_name=partner_name,
                    partner_description=partner_description,
                    partner_basic_info=partner_basic_info,
                    questions=formatted_answers,
                    answers=text_answers,
                    analysis_result=analysis_result
                )
                    logger.info(f"Partner profile saved for user {user_id} (telegram_id: {telegram_id})")
            except Exception as e:
                logger.error(f"Failed to save partner profile: {e}")
            
            # Send results
                logger.info(f"Analysis completed successfully for user {user_id} (telegram_id: {telegram_id})")
            await send_analysis_results(message, analysis_result, pdf_bytes, partner_name)
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            await analysis_msg.edit_text(
                "❌ <b>Ошибка анализа</b>\n\n"
                "Не удалось провести анализ. Попробуйте позже.\n\n"
                f"Техническая информация: {str(e)[:100]}",
                parse_mode="HTML",
                reply_markup=get_profiler_keyboard()
            )
            
    except Exception as e:
        logger.error(f"Error in start_analysis: {e}")
        await message.answer(
            "❌ Произошла критическая ошибка. Попробуйте начать заново.",
            reply_markup=get_profiler_keyboard()
        )
    finally:
        # Clear state
        await state.clear()


@router.callback_query(F.data.startswith("profiler_nav_"))
async def handle_navigation(callback: CallbackQuery, state: FSMContext):
    """Handle profiler navigation"""
    try:
        action = callback.data.split("_")[2]
        
        if action == "back":
            await callback.message.edit_text(
                "🔍 <b>Профайлер партнера</b>\n\n"
                "Выберите действие:",
                parse_mode="HTML",
                reply_markup=profiler_menu_kb()
            )
        elif action == "skip":
            # Handle skip logic if needed
            await callback.answer("Пропуск не поддерживается")
        else:
            await callback.answer("Неизвестная команда")
            
    except Exception as e:
        logger.error(f"Error in navigation: {e}")
        await callback.answer("❌ Произошла ошибка")


@router.callback_query(F.data == "profiler_back")
async def back_to_profiler(callback: CallbackQuery, state: FSMContext, profile_service: ProfileService):
    """Back to profiler menu"""
    await state.clear()
    await show_profiler_menu(callback, state, profile_service)


@router.callback_query(F.data == "profiler_cancel")
async def cancel_profiler(callback: CallbackQuery, state: FSMContext, profile_service: ProfileService):
    """Cancel profiler and return to menu"""
    await state.clear()
    await callback.message.edit_text(
        "❌ <b>Профайлер отменен</b>\n\n"
        "Вы можете начать заново в любое время.",
        parse_mode="HTML"
    )
    await show_profiler_menu(callback, state, profile_service)


@router.callback_query(F.data.startswith("view_profile_"))
async def view_profile_details(callback: CallbackQuery, state: FSMContext, profile_service: ProfileService):
    """View detailed profile information"""
    try:
        profile_id = int(callback.data.split("_")[2])
        
        # Get user from database by telegram_id
        telegram_id = callback.from_user.id
        
        # Get user service from middleware or create session
        from app.core.database import get_session
        from app.services.user_service import UserService
        
        async with get_session() as session:
            user_service = UserService(session)
            user = await user_service.get_user_by_telegram_id(telegram_id)
            
            if not user:
                await callback.message.edit_text(
                    "❌ Пользователь не найден. Используйте /start для регистрации.",
                    reply_markup=get_profiler_keyboard()
                )
                return
        
        user_id = user.id  # Internal database ID
        
        # Get profile details
        profile = await profile_service.get_profile_by_id(profile_id, user_id)
        
        if not profile:
            await callback.answer("❌ Профиль не найден")
            return
        
        # Format profile details
        partner_name = profile.partner_name or f"Партнер #{profile.id}"
        risk_emoji = "🔴" if profile.manipulation_risk >= 7 else "🟡" if profile.manipulation_risk >= 4 else "🟢"
        
        # Build detailed text
        details_text = f"""🔍 <b>Профиль: {partner_name}</b>

{risk_emoji} <b>Риск манипуляций:</b> {profile.manipulation_risk:.1f}/10
⚠️ <b>Уровень срочности:</b> {profile.urgency_level.value}

<b>📋 Описание:</b>
{profile.partner_description or 'Не указано'}

<b>🚨 Красные флаги:</b>"""
        
        # Add red flags
        if profile.red_flags:
            for flag in profile.red_flags[:5]:  # Show first 5
                details_text += f"\n• {flag}"
            if len(profile.red_flags) > 5:
                details_text += f"\n• ... и еще {len(profile.red_flags) - 5}"
        else:
            details_text += "\n• Не обнаружено"
        
        # Add positive traits
        if profile.positive_traits:
            details_text += "\n\n<b>✅ Положительные черты:</b>"
            for trait in profile.positive_traits[:3]:  # Show first 3
                details_text += f"\n• {trait}"
            if len(profile.positive_traits) > 3:
                details_text += f"\n• ... и еще {len(profile.positive_traits) - 3}"
        
        # Add creation date
        details_text += f"\n\n📅 <b>Создан:</b> {profile.created_at.strftime('%d.%m.%Y в %H:%M')}"
        
        # Show buttons
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 К профилям", callback_data="my_profiles")],
            [InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_profile_{profile.id}")]
        ])
        
        await callback.message.edit_text(
            details_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error viewing profile details: {e}")
        await callback.answer("❌ Произошла ошибка")


@router.callback_query(F.data.startswith("recommendations_"))
async def show_detailed_recommendations(callback: CallbackQuery, state: FSMContext, profile_service: ProfileService):
    """Show detailed recommendations for specific profile"""
    try:
        profile_id = int(callback.data.split("_")[1])
        
        # Get user from database by telegram_id
        telegram_id = callback.from_user.id
        
        # Get user service from middleware or create session
        from app.core.database import get_session
        from app.services.user_service import UserService
        
        async with get_session() as session:
            user_service = UserService(session)
            user = await user_service.get_user_by_telegram_id(telegram_id)
            
            if not user:
                await callback.message.edit_text(
                    "❌ Пользователь не найден. Используйте /start для регистрации.",
                    reply_markup=get_profiler_keyboard()
                )
                return
        
        user_id = user.id  # Internal database ID
        
        profile = await profile_service.get_profile_by_id(profile_id, user_id)
        
        if not profile:
            await callback.answer("❌ Профиль не найден")
            return
        
        # Get recommendations for this profile
        recommendations = await profile_service.get_profile_recommendations(profile_id, user_id)
        
        if not recommendations:
            await callback.answer("❌ Не удалось получить рекомендации")
            return
        
        partner_name = profile.partner_name or f"Партнер #{profile.id}"
        
        # Format recommendations
        recommendations_text = f"""💡 <b>Рекомендации для {partner_name}</b>

<b>📊 Анализ профиля:</b>
• Риск манипуляций: {profile.manipulation_risk:.1f}/10
• Уровень срочности: {profile.urgency_level.value}

<b>🎯 Персональные рекомендации:</b>
{recommendations.get('recommendations', 'Рекомендации недоступны')}

<b>⚠️ Что следует помнить:</b>
{recommendations.get('safety_tips', 'Советы недоступны')}"""
        
        # Show back button
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 К рекомендациям", callback_data="profile_recommendations")]
        ])
        
        await callback.message.edit_text(
            recommendations_text,
            parse_mode="HTML", 
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error showing detailed recommendations: {e}")
        await callback.answer("❌ Произошла ошибка")


@router.callback_query(F.data.startswith("delete_profile_"))
async def delete_profile_confirm(callback: CallbackQuery, state: FSMContext):
    """Confirm profile deletion"""
    try:
        profile_id = int(callback.data.split("_")[2])
        
        keyboard = [
            [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_delete_{profile_id}")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data=f"view_profile_{profile_id}")]
        ]
        
        await callback.message.edit_text(
            "🗑️ <b>Удаление профиля</b>\n\n"
            "Вы уверены, что хотите удалить этот профиль?\n\n"
            "❗️ Это действие нельзя отменить.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        
    except Exception as e:
        logger.error(f"Error in delete_profile_confirm: {e}")
        await callback.answer("❌ Произошла ошибка")


@router.callback_query(F.data.startswith("confirm_delete_"))
async def confirm_profile_deletion(callback: CallbackQuery, state: FSMContext, profile_service: ProfileService):
    """Actually delete the profile"""
    try:
        profile_id = int(callback.data.split("_")[2])
        
        # Get user from database by telegram_id
        telegram_id = callback.from_user.id
        
        # Get user service from middleware or create session
        from app.core.database import get_session
        from app.services.user_service import UserService
        
        async with get_session() as session:
            user_service = UserService(session)
            user = await user_service.get_user_by_telegram_id(telegram_id)
            
            if not user:
                await callback.message.edit_text(
                    "❌ Пользователь не найден. Используйте /start для регистрации.",
                    reply_markup=get_profiler_keyboard()
                )
                return
        
        user_id = user.id  # Internal database ID
        
        # Delete profile
        success = await profile_service.delete_profile(profile_id, user_id)
        
        if success:
            await callback.message.edit_text(
                "✅ <b>Профиль удален</b>\n\n"
                "Профиль партнера был успешно удален из базы данных.",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📂 Мои профили", callback_data="my_profiles")]
                ])
            )
            await callback.answer("✅ Профиль удален")
        else:
            await callback.answer("❌ Не удалось удалить профиль")
            
    except Exception as e:
        logger.error(f"Error confirming profile deletion: {e}")
        await callback.answer("❌ Произошла ошибка при удалении")


@router.callback_query(F.data == "start_free_form_questions")
async def start_free_form_questions(callback: CallbackQuery, state: FSMContext):
    """Start free form questions after collecting partner info"""
    try:
        # Get free form questions
        free_form_questions = get_free_form_questions()
        
        # Create question order
        question_order = [
            "narcissism_q1", "narcissism_q2", "narcissism_q3", "narcissism_q4", "narcissism_q5", "narcissism_q6",
            "control_q1", "control_q2", "control_q3", "control_q4", "control_q5", "control_q6",
            "gaslighting_q1", "gaslighting_q2", "gaslighting_q3", "gaslighting_q4", "gaslighting_q5",
            "emotion_q1", "emotion_q2", "emotion_q3", "emotion_q4",
            "intimacy_q1", "intimacy_q2", "intimacy_q3",
            "social_q1", "social_q2", "social_q3", "social_q4"
        ]
        
        # Update state with questions data
        await state.set_state(FreeFormProfilerStates.narcissism_q1_text)
        await state.update_data(
            free_form_questions=free_form_questions,
            question_order=question_order,
            current_question=0,
            text_answers={}
        )
        
        # Send first question
        first_question = free_form_questions["narcissism_q1"]
        
        data = await state.get_data()
        partner_name = data.get('partner_name', 'партнера')
        
        await callback.message.edit_text(
            f"🎯 <b>Вопрос 1 из 28</b> (Свободная форма)\n\n"
            f"📝 <b>О {partner_name}:</b>\n\n"
            f"❓ <b>{first_question['text']}</b>\n\n"
            f"💭 <i>{first_question['context']}</i>\n\n"
            f"🔍 <b>Подсказки для ответа:</b>\n"
            + "\n".join([f"• {hint}" for hint in first_question['prompt_hints']]) + "\n\n"
            f"💡 <b>Пример ответа:</b>\n"
            f"<i>{first_question['example']}</i>\n\n"
            f"✏️ <b>Напишите ваш ответ:</b>\n"
            f"<i>Минимум {first_question['min_length']} символов</i>",
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error in start_free_form_questions: {e}")
        await callback.answer("❌ Произошла ошибка")


async def send_analysis_results(message: Message, analysis_result: Dict[str, Any], pdf_bytes: bytes, partner_name: str):
    """Send analysis results to user"""
    try:
        # Extract key metrics
        overall_risk_percent = analysis_result.get('overall_risk_score', 0)
        urgency_level = analysis_result.get('urgency_level', 'LOW')
        block_scores = analysis_result.get('block_scores', {})
        
        # Risk level emoji and message
        if overall_risk_percent >= 75:
            risk_emoji = "🔴"
            risk_level = "КРИТИЧЕСКИЙ"
            risk_message = "⚠️ <b>Немедленно обратитесь к специалисту!</b>"
        elif overall_risk_percent >= 50:
            risk_emoji = "🟠"
            risk_level = "ВЫСОКИЙ"
            risk_message = "⚠️ <b>Рекомендуется консультация психолога</b>"
        elif overall_risk_percent >= 25:
            risk_emoji = "🟡"
            risk_level = "СРЕДНИЙ"
            risk_message = "💡 <b>Стоит обратить внимание на некоторые моменты</b>"
        else:
            risk_emoji = "🟢"
            risk_level = "НИЗКИЙ"
            risk_message = "✅ <b>Отношения в целом здоровые</b>"
        
        # Build scores text
        block_names = {
            "narcissism": "Нарциссизм",
            "control": "Контроль",
            "gaslighting": "Газлайтинг",
            "emotion": "Эмоции",
            "intimacy": "Интимность",
            "social": "Социальное поведение"
        }
        
        scores_text = ""
        for block, score in block_scores.items():
            block_name = block_names.get(block, block)
            scores_text += f"• {block_name}: {score:.1f}/10\n"
        
        # Create summary message
        summary_text = f"""📊 <b>Психологический анализ завершен</b>

👤 <b>Партнер:</b> {partner_name}
📝 <b>Формат:</b> Детальные ответы (28 вопросов)

{risk_emoji} <b>Уровень риска:</b> {risk_level} ({overall_risk_percent}%)

{risk_message}

<b>Детальные оценки:</b>
{scores_text}

📄 <b>Расширенный отчет отправлен отдельным файлом</b>
<b>Качество анализа:</b> Максимальное (свободная форма)"""
        
        # Send summary
        await message.answer(
            summary_text,
            parse_mode="HTML",
            reply_markup=get_profiler_keyboard()
        )
        
        # Send PDF report
        try:
            from aiogram.types import BufferedInputFile
            
            pdf_file = BufferedInputFile(
                pdf_bytes,
                filename=f"free_form_profile_{partner_name}_{message.from_user.id}.pdf"
            )
        
            await message.answer_document(
                document=pdf_file,
                caption=f"📄 Профессиональный психологический анализ партнера {partner_name}\n"
                       f"📝 Основан на 28 развернутых ответах с применением методик DSM-5, ICD-11 и Dark Triad"
            )
            logger.info(f"Free form PDF report sent successfully for user {message.from_user.id}")
            
        except Exception as pdf_error:
            logger.error(f"Error sending free form PDF: {pdf_error}")
            await message.answer(
                "📄 PDF отчет сгенерирован, но не удалось отправить. Попробуйте еще раз.",
                reply_markup=get_profiler_keyboard()
            )
            
    except Exception as e:
        logger.error(f"Error in send_analysis_results: {e}")
        await message.answer(
            "❌ Ошибка при отправке результатов",
            reply_markup=get_profiler_keyboard()
        )