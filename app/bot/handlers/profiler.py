"""Profiler handler for partner analysis"""

import asyncio
from typing import Dict, Any
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from loguru import logger

from app.bot.states import ProfilerStates, PartnerProfileStates
from app.bot.keyboards.inline import profiler_menu_kb, get_profiler_keyboard, get_profiler_navigation_keyboard, get_profiler_question_keyboard
from app.services.ai_service import AIService
from app.services.html_pdf_service import HTMLPDFService
from app.services.user_service import UserService
from app.services.profile_service import ProfileService
from app.utils.exceptions import ServiceError
from app.utils.enums import AnalysisType
from app.prompts.profiler_full_questions import get_all_questions

router = Router()


@router.callback_query(F.data == "profiler_menu")
async def show_profiler_menu(callback: CallbackQuery, state: FSMContext, profile_service: ProfileService):
    """Show profiler menu"""
    try:
        await state.clear()
        user_id = callback.from_user.id
        
        # Get user's profiles for statistics
        profiles = await profile_service.get_user_profiles(user_id, limit=10)
        
        # Build profiler menu text with statistics
        menu_text = "🔍 <b>Профайлер партнера</b>\n\n"
        
        if profiles:
            # Statistics
            total_profiles = len(profiles)
            high_risk = len([p for p in profiles if p.manipulation_risk >= 7])
            medium_risk = len([p for p in profiles if 4 <= p.manipulation_risk < 7])
            low_risk = len([p for p in profiles if p.manipulation_risk < 4])
            
            menu_text += f"📊 <b>Ваша статистика:</b>\n"
            menu_text += f"• Всего профилей: {total_profiles}\n"
            
            if high_risk > 0:
                menu_text += f"• 🔴 Высокий риск: {high_risk}\n"
            if medium_risk > 0:
                menu_text += f"• 🟡 Средний риск: {medium_risk}\n"
            if low_risk > 0:
                menu_text += f"• 🟢 Низкий риск: {low_risk}\n"
            
            menu_text += "\n"
            
            # Latest profiles
            menu_text += f"📋 <b>Последние профили:</b>\n"
            for i, profile in enumerate(profiles[:3], 1):
                risk_emoji = "🔴" if profile.manipulation_risk >= 7 else "🟡" if profile.manipulation_risk >= 4 else "🟢"
                partner_name = profile.partner_name or f"Партнер #{profile.id}"
                menu_text += f"{i}. {risk_emoji} {partner_name} ({profile.manipulation_risk:.1f}/10)\n"
            menu_text += "\n"
            
            # Quick recommendations
            if high_risk > 0:
                menu_text += "⚠️ <b>Важное уведомление:</b>\n"
                menu_text += "Обнаружены высокорисковые профили. Рекомендуется проконсультироваться с психологом.\n\n"
            elif medium_risk > 0:
                menu_text += "💡 <b>Рекомендация:</b>\n"
                menu_text += "Изучите красные флаги в отношениях и развивайте эмоциональный интеллект.\n\n"
            else:
                menu_text += "✅ <b>Статус:</b>\n"
                menu_text += "Хорошие показатели! Продолжайте развивать здоровые отношения.\n\n"
        else:
            menu_text += "👋 <b>Добро пожаловать!</b>\n\n"
            menu_text += "Профайлер партнера поможет вам:\n"
            menu_text += "• 🔍 Проанализировать поведение партнера\n"
            menu_text += "• 🚨 Выявить красные флаги\n"
            menu_text += "• 💡 Получить персональные рекомендации\n"
            menu_text += "• 📊 Оценить совместимость\n\n"
            menu_text += "Создайте первый профиль, чтобы начать анализ.\n\n"
        
        menu_text += "Выберите действие:"
        
        await callback.message.edit_text(
            menu_text,
            parse_mode="HTML",
            reply_markup=profiler_menu_kb()
        )
    except Exception as e:
        logger.error(f"Error showing profiler menu: {e}")
        await callback.answer("❌ Произошла ошибка")


@router.callback_query(F.data == "create_profile")
async def create_new_profile(callback: CallbackQuery, state: FSMContext):
    """Create new profile - show introduction and start data collection"""
    try:
        await callback.message.edit_text(
            "📝 <b>Создание профиля партнера</b>\n\n"
            "🎯 <b>Что будет происходить:</b>\n"
            "• Сначала расскажите о партнере\n"
            "• Затем ответите на 28 вопросов\n"
            "• Получите детальный анализ\n"
            "• Узнаете уровень риска\n"
            "• Получите персональные рекомендации\n\n"
            "⏱️ <b>Время:</b> 10-15 минут\n"
            "🔒 <b>Конфиденциальность:</b> Все данные защищены\n\n"
            "Готовы начать?",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🚀 Начать", callback_data="start_partner_info")],
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
        
        await message.answer(
            f"✅ <b>Информация о {partner_name} сохранена</b>\n\n"
            "🎯 <b>Переходим к вопросам</b>\n\n"
            "Сейчас вам будет предложено 28 вопросов о поведении партнера.\n"
            "Отвечайте честно - это поможет получить точный анализ.\n\n"
            "⏱️ <b>Время:</b> 8-10 минут\n"
            "🔒 <b>Конфиденциально:</b> Никто не увидит ваши ответы",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🚀 Начать вопросы", callback_data="start_questions_now")],
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
        await callback.message.edit_text(
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
        logger.error(f"Error in back_to_basic_info_input: {e}")
        await callback.answer("❌ Произошла ошибка")


@router.callback_query(F.data == "start_questions_now")
async def start_questions_now(callback: CallbackQuery, state: FSMContext):
    """Start profiler questions after collecting partner info"""
    try:
        # Get all questions
        questions = get_all_questions()
        from app.prompts.profiler_full_questions import QUESTION_ORDER
        
        # Update state with questions data
        await state.set_state(ProfilerStates.answering_questions)
        await state.update_data(
            questions=questions,
            question_order=QUESTION_ORDER,
            current_question=0,
            answers={}
        )
        
        # Send first question
        first_question_id = QUESTION_ORDER[0]
        first_question = questions[first_question_id]
        
        data = await state.get_data()
        partner_name = data.get('partner_name', 'партнера')
        
        # Get block name in Russian
        block_names = {
            "narcissism": "Нарциссизм и грандиозность",
            "control": "Контроль и манипуляции",
            "gaslighting": "Газлайтинг и искажение реальности",
            "emotion": "Эмоциональная регуляция",
            "intimacy": "Интимность и принуждение",
            "social": "Социальное поведение"
        }
        
        block_name = block_names.get(first_question['block'], first_question['block'])
        
        await callback.message.edit_text(
            f"🎯 <b>Вопрос 1 из 28</b>\n\n"
            f"📝 <b>О {partner_name}:</b>\n\n"
            f"{first_question['text']}\n\n"
            f"🔍 <b>Блок:</b> {block_name}\n"
            f"💡 <i>{first_question['context']}</i>",
            parse_mode="HTML",
            reply_markup=get_profiler_question_keyboard(first_question_id, first_question['options'])
        )
        
    except Exception as e:
        logger.error(f"Error in start_questions_now: {e}")
        await callback.answer("❌ Произошла ошибка")


@router.callback_query(F.data == "my_profiles")
async def show_my_profiles(callback: CallbackQuery, state: FSMContext, profile_service: ProfileService):
    """Show user's existing profiles"""
    try:
        user_id = callback.from_user.id
        
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
    """Show profile recommendations"""
    try:
        user_id = callback.from_user.id
        
        # Get user's profiles
        profiles = await profile_service.get_user_profiles(user_id, limit=5)
        
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





@router.callback_query(F.data.startswith("answer_"))
async def handle_answer(callback: CallbackQuery, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    """Handle user answer to profiling question"""
    try:
        # Parse callback data: answer_{question_id}_{answer_index}
        # Question ID can contain underscores, so we split and take the last part as answer_index
        callback_parts = callback.data.split("_")
        if len(callback_parts) < 3:
            await callback.answer("❌ Неверный формат ответа")
            return
            
        # Last part is answer_index, everything between "answer" and last part is question_id
        answer_index = int(callback_parts[-1])
        question_id = "_".join(callback_parts[1:-1])
        
        # Get state data
        data = await state.get_data()
        questions = data.get('questions', {})
        question_order = data.get('question_order', [])
        current_question = data.get('current_question', 0)
        answers = data.get('answers', {})
        
        # Save answer
        answers[question_id] = answer_index
        logger.info(f"Saved answer for question {question_id}: {answer_index}")
        
        # Move to next question
        next_question = current_question + 1
        logger.info(f"Moving to question {next_question + 1} of {len(question_order)}")
        
        if next_question < len(question_order):
            # Update state
            await state.update_data(
                current_question=next_question,
                answers=answers
            )
            
            # Send next question
            next_question_id = question_order[next_question]
            question = questions.get(next_question_id)
            
            if not question:
                logger.error(f"Question {next_question_id} not found in questions dict")
                await callback.answer("❌ Вопрос не найден")
                return
            
            # Get partner name
            partner_name = data.get('partner_name', 'партнера')
            
            # Get block name
            block_names = {
                "narcissism": "Нарциссизм и грандиозность",
                "control": "Контроль и манипуляции",
                "gaslighting": "Газлайтинг и искажение реальности",
                "emotion": "Эмоциональная регуляция",
                "intimacy": "Интимность и принуждение",
                "social": "Социальное поведение"
            }
            block_name = block_names.get(question['block'], question['block'])
            
            await callback.message.edit_text(
                f"🎯 <b>Вопрос {next_question + 1} из {len(question_order)}</b>\n\n"
                f"📝 <b>О {partner_name}:</b>\n\n"
                f"{question['text']}\n\n"
                f"🔍 <b>Блок:</b> {block_name}\n"
                f"💡 <i>{question['context']}</i>",
                parse_mode="HTML",
                reply_markup=get_profiler_question_keyboard(next_question_id, question['options'])
            )
        else:
            # All questions answered - start analysis
            await state.update_data(answers=answers)
            await start_analysis(callback.message, state, ai_service, html_pdf_service, user_service, profile_service)
            
    except Exception as e:
        logger.error(f"Error handling answer: {e}")
        await callback.answer("❌ Произошла ошибка при обработке ответа")


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


async def start_analysis(message: Message, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    """Start AI analysis of answers"""
    try:
        # Get user data
        user_id = message.from_user.id
        data = await state.get_data()
        answers = data.get('answers', {})
        
        # Get partner info from state
        partner_name = data.get('partner_name', 'Партнер')
        partner_description = data.get('partner_description', '')
        partner_basic_info = data.get('partner_basic_info', '')
        
        # Send analysis start message
        analysis_msg = await message.answer(
            f"🔍 <b>Анализ профиля {partner_name}</b>\n\n"
            "⏳ Обрабатываю ваши ответы...\n"
            "📊 Провожу психологический анализ...\n"
            "🎯 Выявляю красные флаги...\n\n"
            "<i>Это может занять до 2 минут</i>",
            parse_mode="HTML"
        )
        
        # Convert answers to format expected by AI service
        formatted_answers = []
        questions = data.get('questions', {})
        for question_id, answer_index in answers.items():
            question = questions.get(question_id, {})
            options = question.get('options', [])
            if answer_index < len(options):
                formatted_answers.append({
                    'question_id': question_id,
                    'question': question.get('text', ''),
                    'answer': options[answer_index]
                })
        
        # Perform AI analysis
        try:
            analysis_result = await ai_service.profile_partner(
                answers=formatted_answers, 
                user_id=user_id, 
                partner_name=partner_name,
                partner_description=partner_description
            )
            
            # Update progress
            await analysis_msg.edit_text(
                f"🔍 <b>Анализ профиля {partner_name}</b>\n\n"
                "✅ Психологический профиль готов\n"
                "📋 Генерирую PDF отчет...\n\n"
                "<i>Почти готово!</i>",
                parse_mode="HTML"
            )
            
            # Generate PDF report
            pdf_bytes = await html_pdf_service.generate_partner_report_html(
                analysis_result,
                user_id,
                partner_name
            )
            
            # Save analysis to database (legacy format)
            try:
                await user_service.save_analysis(
                    user_id=user_id,
                    analysis_type=AnalysisType.PARTNER_PROFILE,
                    analysis_data=analysis_result,
                    questions=formatted_answers
                )
            except Exception as e:
                logger.warning(f"Failed to save analysis to DB: {e}")
            
            # Save partner profile to database
            try:
                await profile_service.create_profile_from_profiler(
                    user_id=user_id,
                    partner_name=partner_name,
                    partner_description=partner_description,
                    partner_basic_info=partner_basic_info,
                    questions=formatted_answers,
                    answers=answers,
                    analysis_result=analysis_result
                )
                logger.info(f"Partner profile saved for user {user_id}")
            except Exception as e:
                logger.error(f"Failed to save partner profile: {e}")
            
            # Send results
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


async def send_analysis_results(
    message: Message,
    analysis_result: Dict[str, Any],
    pdf_bytes: bytes,
    partner_name: str
):
    """Send analysis results to user"""
    try:
        # Extract key metrics
        overall_risk = analysis_result.get('overall_risk_score', analysis_result.get('manipulation_risk', 0))
        
        # Convert to percentage if needed
        if isinstance(overall_risk, float) and overall_risk <= 10:
            overall_risk_percent = int(overall_risk * 10)  # Convert 0-10 scale to 0-100
        else:
            overall_risk_percent = int(overall_risk)
            
        urgency_level = analysis_result.get('urgency_level', 'UNKNOWN')
        block_scores = analysis_result.get('block_scores', {})
        
        # Determine risk emoji and message
        if overall_risk_percent >= 80:
            risk_emoji = "🚨"
            risk_level = "КРИТИЧЕСКИЙ"
            risk_message = "Обнаружены серьезные признаки токсичного поведения!"
        elif overall_risk_percent >= 60:
            risk_emoji = "⚠️"
            risk_level = "ВЫСОКИЙ"
            risk_message = "Выявлены значительные проблемы в поведении партнера."
        elif overall_risk_percent >= 40:
            risk_emoji = "🟡"
            risk_level = "СРЕДНИЙ"
            risk_message = "Есть некоторые тревожные признаки."
        else:
            risk_emoji = "✅"
            risk_level = "НИЗКИЙ"
            risk_message = "Серьезных проблем не обнаружено."
        
        # Format block scores
        block_names = {
            'narcissism': 'Нарциссизм',
            'control': 'Контроль',
            'gaslighting': 'Газлайтинг',
            'emotion': 'Эмоции',
            'intimacy': 'Интимность',
            'social': 'Социальное'
        }
        
        scores_text = ""
        for block, score in block_scores.items():
            block_name = block_names.get(block, block)
            # Round to 1 decimal place
            scores_text += f"• {block_name}: {score:.1f}/10\n"
        
        # Create summary message
        summary_text = f"""📊 <b>Анализ завершен</b>

👤 <b>Партнер:</b> {partner_name}

{risk_emoji} <b>Уровень риска:</b> {risk_level} ({overall_risk_percent}%)

{risk_message}

<b>Детальные оценки:</b>
{scores_text}

📄 Подробный отчет отправлен отдельным файлом."""
        
        # Send summary
        await message.answer(
            summary_text,
            parse_mode="HTML",
            reply_markup=get_profiler_keyboard()
        )
        
                # Send PDF report
        try:
            from aiogram.types import BufferedInputFile
            
            # Create BufferedInputFile for PDF
            pdf_file = BufferedInputFile(
                pdf_bytes,
                filename=f"profile_{partner_name}_{message.from_user.id}.pdf"
            )
            
            await message.answer_document(
                document=pdf_file,
                caption=f"📄 Полный психологический профиль партнера {partner_name}",
                reply_markup=get_profiler_keyboard()
            )
            logger.info(f"PDF report sent successfully for user {message.from_user.id}")
            
        except Exception as pdf_error:
            logger.error(f"Error sending PDF: {pdf_error}")
            await message.answer(
                "📄 PDF отчет сгенерирован, но не удалось отправить. Попробуйте еще раз.",
                reply_markup=get_profiler_keyboard()
            )
        
    except Exception as e:
        logger.error(f"Error sending analysis results: {e}")
        await message.answer(
            "❌ Ошибка при отправке результатов анализа.",
            reply_markup=get_profiler_keyboard()
        )


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
        user_id = callback.from_user.id
        
        # Get profile details
        profile = await profile_service.get_profile_by_id(profile_id, user_id)
        
        if not profile:
            await callback.answer("❌ Профиль не найден")
            return
        
        # Build profile details text
        partner_name = profile.partner_name or f"Партнер #{profile.id}"
        risk_emoji = "🔴" if profile.manipulation_risk >= 7 else "🟡" if profile.manipulation_risk >= 4 else "🟢"
        
        profile_text = f"📋 <b>{partner_name}</b>\n\n"
        profile_text += f"{risk_emoji} <b>Оценка риска:</b> {profile.manipulation_risk:.1f}/10\n"
        profile_text += f"📅 <b>Создан:</b> {profile.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        
        # Risk assessment
        if profile.manipulation_risk >= 7:
            profile_text += "🚨 <b>ВЫСОКИЙ РИСК</b>\n"
            profile_text += "Обнаружены серьезные тревожные сигналы. Рекомендуется осторожность.\n\n"
        elif profile.manipulation_risk >= 4:
            profile_text += "⚠️ <b>СРЕДНИЙ РИСК</b>\n"
            profile_text += "Есть некоторые тревожные моменты. Стоит обратить внимание.\n\n"
        else:
            profile_text += "✅ <b>НИЗКИЙ РИСК</b>\n"
            profile_text += "В целом безопасный партнер. Хорошие показатели.\n\n"
        
        # Red flags
        if profile.red_flags:
            profile_text += "🚩 <b>Красные флаги:</b>\n"
            for flag in profile.red_flags[:5]:  # Top 5
                profile_text += f"• {flag}\n"
            profile_text += "\n"
        
        # Positive traits
        if profile.positive_traits:
            profile_text += "✨ <b>Положительные черты:</b>\n"
            for trait in profile.positive_traits[:5]:  # Top 5
                profile_text += f"• {trait}\n"
            profile_text += "\n"
        
        # Recommendations
        if profile.relationship_advice:
            profile_text += f"💡 <b>Рекомендации:</b>\n{profile.relationship_advice[:300]}...\n\n"
        
        # Create keyboard
        keyboard = [
            [InlineKeyboardButton(text="📊 Детальный анализ", callback_data=f"detailed_analysis_{profile_id}")],
            [InlineKeyboardButton(text="💡 Рекомендации", callback_data=f"recommendations_{profile_id}")],
            [InlineKeyboardButton(text="🗑️ Удалить профиль", callback_data=f"delete_profile_{profile_id}")],
            [InlineKeyboardButton(text="🔙 К списку профилей", callback_data="my_profiles")]
        ]
        
        await callback.message.edit_text(
            profile_text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        
    except Exception as e:
        logger.error(f"Error viewing profile details: {e}")
        await callback.answer("❌ Произошла ошибка при загрузке профиля")


@router.callback_query(F.data.startswith("recommendations_"))
async def show_detailed_recommendations(callback: CallbackQuery, state: FSMContext, profile_service: ProfileService):
    """Show detailed recommendations for specific profile"""
    try:
        profile_id = int(callback.data.split("_")[1])
        user_id = callback.from_user.id
        
        # Get profile details
        profile = await profile_service.get_profile_by_id(profile_id, user_id)
        
        if not profile:
            await callback.answer("❌ Профиль не найден")
            return
        
        partner_name = profile.partner_name or f"Партнер #{profile.id}"
        risk_emoji = "🔴" if profile.manipulation_risk >= 7 else "🟡" if profile.manipulation_risk >= 4 else "🟢"
        
        # Build recommendations text
        rec_text = f"💡 <b>Рекомендации для {partner_name}</b>\n\n"
        rec_text += f"{risk_emoji} <b>Уровень риска:</b> {profile.manipulation_risk:.1f}/10\n\n"
        
        # Risk-based recommendations
        if profile.manipulation_risk >= 7:
            rec_text += "🚨 <b>КРИТИЧЕСКИ ВАЖНО:</b>\n"
            rec_text += "• Обратитесь к психологу или консультанту\n"
            rec_text += "• Не игнорируйте красные флаги\n"
            rec_text += "• Установите четкие границы\n"
            rec_text += "• Подумайте о безопасности выхода из отношений\n\n"
        elif profile.manipulation_risk >= 4:
            rec_text += "⚠️ <b>РЕКОМЕНДУЕТСЯ:</b>\n"
            rec_text += "• Изучите техники распознавания манипуляций\n"
            rec_text += "• Обратите внимание на паттерны поведения\n"
            rec_text += "• Развивайте эмоциональную независимость\n"
            rec_text += "• Обсудите проблемы с доверенными людьми\n\n"
        else:
            rec_text += "✅ <b>ПОДДЕРЖИВАЙТЕ:</b>\n"
            rec_text += "• Продолжайте строить здоровые отношения\n"
            rec_text += "• Развивайте открытое общение\n"
            rec_text += "• Цените взаимное уважение\n"
            rec_text += "• Изучайте психологию совместимости\n\n"
        
        # Specific recommendations
        if profile.relationship_advice:
            rec_text += f"📋 <b>Персональные советы:</b>\n{profile.relationship_advice}\n\n"
        
        # Communication tips
        if profile.communication_tips:
            rec_text += f"💬 <b>Советы по общению:</b>\n{profile.communication_tips}\n\n"
        
        # Warning signs
        if profile.warning_signs:
            rec_text += "🚨 <b>На что обратить внимание:</b>\n"
            for warning in profile.warning_signs[:5]:
                rec_text += f"• {warning}\n"
            rec_text += "\n"
        
        # Create keyboard
        keyboard = [
            [InlineKeyboardButton(text="📋 Профиль", callback_data=f"view_profile_{profile_id}")],
            [InlineKeyboardButton(text="📊 Детальный анализ", callback_data=f"detailed_analysis_{profile_id}")],
            [InlineKeyboardButton(text="🔙 К списку профилей", callback_data="my_profiles")]
        ]
        
        await callback.message.edit_text(
            rec_text,
            parse_mode="HTML", 
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        
    except Exception as e:
        logger.error(f"Error showing detailed recommendations: {e}")
        await callback.answer("❌ Произошла ошибка при загрузке рекомендаций")


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
        user_id = callback.from_user.id
        
        # Delete profile
        success = await profile_service.delete_profile(profile_id, user_id)
        
        if success:
            await callback.message.edit_text(
                "✅ <b>Профиль удален</b>\n\n"
                "Профиль успешно удален из вашего списка.",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📂 Мои профили", callback_data="my_profiles")],
                    [InlineKeyboardButton(text="🔙 В меню", callback_data="profiler_menu")]
                ])
            )
        else:
            await callback.answer("❌ Не удалось удалить профиль")
            
    except Exception as e:
        logger.error(f"Error confirming profile deletion: {e}")
        await callback.answer("❌ Произошла ошибка при удалении")