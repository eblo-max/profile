"""Profiler handler for partner analysis"""

import asyncio
from typing import Dict, Any
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from loguru import logger

from app.bot.states import ProfilerStates
from app.bot.keyboards.inline import profiler_menu_kb, get_profiler_keyboard, get_profiler_navigation_keyboard
from app.services.ai_service import AIService
from app.services.html_pdf_service import HTMLPDFService
from app.services.user_service import UserService
from app.services.profile_service import ProfileService
from app.utils.exceptions import ServiceError
from app.utils.enums import AnalysisType
from app.prompts.profiler_full_questions import get_all_questions

router = Router()


@router.callback_query(F.data == "profiler_menu")
async def show_profiler_menu(callback: CallbackQuery, state: FSMContext):
    """Show profiler menu"""
    try:
        await state.clear()
        await callback.message.edit_text(
            "🔍 <b>Профайлер партнера</b>\n\n"
            "Выберите действие:",
            parse_mode="HTML",
            reply_markup=profiler_menu_kb()
        )
    except Exception as e:
        logger.error(f"Error showing profiler menu: {e}")
        await callback.answer("❌ Произошла ошибка")


@router.callback_query(F.data == "create_profile")
async def create_new_profile(callback: CallbackQuery, state: FSMContext):
    """Create new profile - show options"""
    try:
        await callback.message.edit_text(
            "📝 <b>Создание нового профиля</b>\n\n"
            "Выберите тип профилирования:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🎯 Полный профиль (28 вопросов)", callback_data="start_profiler_full")],
                [InlineKeyboardButton(text="🔙 Назад", callback_data="profiler_menu")]
            ])
        )
    except Exception as e:
        logger.error(f"Error in create_new_profile: {e}")
        await callback.answer("❌ Произошла ошибка")


@router.callback_query(F.data == "my_profiles")
async def show_my_profiles(callback: CallbackQuery, state: FSMContext):
    """Show user's existing profiles"""
    try:
        await callback.message.edit_text(
            "📂 <b>Мои профили</b>\n\n"
            "🚧 Функция в разработке\n\n"
            "Здесь будут отображаться ваши сохраненные профили партнеров.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="profiler_menu")]
            ])
        )
    except Exception as e:
        logger.error(f"Error in show_my_profiles: {e}")
        await callback.answer("❌ Произошла ошибка")


@router.callback_query(F.data == "profile_recommendations")
async def show_profile_recommendations(callback: CallbackQuery, state: FSMContext):
    """Show profile recommendations"""
    try:
        await callback.message.edit_text(
            "💡 <b>Рекомендации</b>\n\n"
            "🚧 Функция в разработке\n\n"
            "Здесь будут персональные рекомендации на основе ваших профилей.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="profiler_menu")]
            ])
        )
    except Exception as e:
        logger.error(f"Error in show_profile_recommendations: {e}")
        await callback.answer("❌ Произошла ошибка")


@router.callback_query(F.data == "start_profiler_full")
async def start_profiler_full(callback: CallbackQuery, state: FSMContext):
    """Start full profiler process"""
    try:
        # Get all questions
        questions = get_all_questions()
        question_order = [
            "narcissism_q1", "narcissism_q2", "narcissism_q3", "narcissism_q4", "narcissism_q5", "narcissism_q6",
            "control_q1", "control_q2", "control_q3", "control_q4", "control_q5", "control_q6",
            "gaslighting_q1", "gaslighting_q2", "gaslighting_q3", "gaslighting_q4", "gaslighting_q5",
            "emotion_q1", "emotion_q2", "emotion_q3", "emotion_q4",
            "intimacy_q1", "intimacy_q2", "intimacy_q3",
            "social_q1", "social_q2", "social_q3", "social_q4"
        ]
        
        # Initialize state
        await state.set_state(ProfilerStates.answering_questions)
        await state.update_data(
            questions=questions,
            question_order=question_order,
            current_question=0,
            answers={}
        )
        
        # Send first question
        first_question_id = question_order[0]
        first_question = questions[first_question_id]
        
        # Format question text
        question_text = f"""🔍 <b>Профайлинг партнера</b>

📋 Вопрос 1 из {len(question_order)}

🧠 <b>Блок:</b> Нарциссизм и грандиозность

<b>{first_question['text']}</b>

💭 <i>{first_question['context']}</i>

Выберите наиболее подходящий вариант:"""
        
        # Create options keyboard
        options = []
        for i, option in enumerate(first_question['options']):
            options.append([InlineKeyboardButton(text=f"{i+1}. {option[:50]}{'...' if len(option) > 50 else ''}", callback_data=f"answer_{i}")])
        
        options.append([InlineKeyboardButton(text="🔙 Назад", callback_data="profiler_menu")])
        
        await callback.message.edit_text(
            question_text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=options)
        )
        
    except Exception as e:
        logger.error(f"Error starting full profiler: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при запуске профайлера. Попробуйте позже.",
            reply_markup=profiler_menu_kb()
        )


@router.callback_query(F.data.startswith("answer_"))
async def handle_answer(callback: CallbackQuery, state: FSMContext, ai_service: AIService, html_pdf_service: HTMLPDFService, user_service: UserService, profile_service: ProfileService):
    """Handle user answer to profiling question"""
    try:
        # Get answer index
        answer_index = int(callback.data.split("_")[1])
        
        # Get state data
        data = await state.get_data()
        questions = data.get('questions', {})
        question_order = data.get('question_order', [])
        current_question = data.get('current_question', 0)
        answers = data.get('answers', {})
        
        # Save answer
        current_question_id = question_order[current_question]
        answers[current_question_id] = answer_index
        
        # Move to next question
        next_question = current_question + 1
        
        if next_question < len(question_order):
            # Update state
            await state.update_data(
                current_question=next_question,
                answers=answers
            )
            
            # Send next question
            next_question_id = question_order[next_question]
            question = questions[next_question_id]
            
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
            
            # Format question text
            question_text = f"""🔍 <b>Профайлинг партнера</b>

📋 Вопрос {next_question + 1} из {len(question_order)}

{get_block_emoji(question['block'])} <b>Блок:</b> {block_name}

<b>{question['text']}</b>

💭 <i>{question['context']}</i>

Выберите наиболее подходящий вариант:"""
            
            # Create options keyboard
            options = []
            for i, option in enumerate(question['options']):
                options.append([InlineKeyboardButton(text=f"{i+1}. {option[:50]}{'...' if len(option) > 50 else ''}", callback_data=f"answer_{i}")])
            
            options.append([InlineKeyboardButton(text="🔙 Назад", callback_data="profiler_menu")])
            
            await callback.message.edit_text(
                question_text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=options)
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
        
        # Get partner name if available
        partner_name = "Партнер"
        try:
            user_profile = await profile_service.get_profile(user_id)
            if user_profile and user_profile.partner_name:
                partner_name = user_profile.partner_name
        except:
            pass
        
        # Send analysis start message
        analysis_msg = await message.answer(
            "🔍 <b>Анализ начат</b>\n\n"
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
            analysis_result = await ai_service.profile_partner(formatted_answers, user_id)
            
            # Update progress
            await analysis_msg.edit_text(
                "🔍 <b>Анализ завершен</b>\n\n"
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
            
            # Save analysis to database
            try:
                await user_service.save_analysis(
                    user_id=user_id,
                    analysis_type=AnalysisType.PARTNER_PROFILE,
                    analysis_data=analysis_result,
                    questions=formatted_answers
                )
            except Exception as e:
                logger.warning(f"Failed to save analysis to DB: {e}")
            
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
        overall_risk = analysis_result.get('overall_risk_score', 0)
        urgency_level = analysis_result.get('urgency_level', 'UNKNOWN')
        block_scores = analysis_result.get('block_scores', {})
        
        # Determine risk emoji and message
        if overall_risk >= 80:
            risk_emoji = "🚨"
            risk_level = "КРИТИЧЕСКИЙ"
            risk_message = "Обнаружены серьезные признаки токсичного поведения!"
        elif overall_risk >= 60:
            risk_emoji = "⚠️"
            risk_level = "ВЫСОКИЙ"
            risk_message = "Выявлены значительные проблемы в поведении партнера."
        elif overall_risk >= 40:
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
            scores_text += f"• {block_name}: {score}/10\n"
        
        # Create summary message
        summary_text = f"""📊 <b>Анализ завершен</b>

👤 <b>Партнер:</b> {partner_name}

{risk_emoji} <b>Уровень риска:</b> {risk_level} ({overall_risk}%)

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
        from io import BytesIO
        pdf_file = BytesIO(pdf_bytes)
        pdf_file.name = f"profile_{partner_name}_{message.from_user.id}.pdf"
        
        await message.answer_document(
            document=pdf_file,
            caption=f"📄 Полный психологический профиль партнера {partner_name}",
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
async def back_to_profiler(callback: CallbackQuery, state: FSMContext):
    """Go back to profiler menu"""
    try:
        await state.clear()
        await callback.message.edit_text(
            "🔍 <b>Профайлер партнера</b>\n\n"
            "Выберите действие:",
            parse_mode="HTML",
            reply_markup=profiler_menu_kb()
        )
    except Exception as e:
        logger.error(f"Error going back to profiler: {e}")
        await callback.answer("❌ Произошла ошибка")