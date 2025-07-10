"""Profiler handler for partner analysis"""

import asyncio
from typing import Dict, Any
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from loguru import logger

from app.bot.states import ProfilerStates
from app.bot.keyboards.inline import get_profiler_keyboard, get_profiler_navigation_keyboard
from app.bot.middlewares.dependencies import get_dependencies
from app.services.ai_service import AIService
from app.services.html_pdf_service import HTMLPDFService
from app.services.user_service import UserService
from app.services.profile_service import ProfileService
from app.utils.exceptions import ServiceError
from app.utils.enums import AnalysisType
from app.prompts.profiler_full_questions import get_all_questions


router = Router()


@router.callback_query(F.data == "profiler_full")
async def start_profiler(callback: CallbackQuery, state: FSMContext):
    """Start partner profiling process"""
    try:
        await callback.answer()
        
        # Get all questions
        questions = get_all_questions()
        
        # Initialize state
        await state.set_state(ProfilerStates.answering_questions)
        await state.update_data(
            questions=questions,
            current_question=0,
            answers=[]
        )
        
        # Send first question
        first_question = questions[0]
        await callback.message.edit_text(
            f"🔍 <b>Профайлинг партнера</b>\n\n"
            f"Вопрос 1 из {len(questions)}:\n\n"
            f"<b>{first_question['question']}</b>\n\n"
            f"💡 {first_question['hint']}",
            parse_mode="HTML",
            reply_markup=get_profiler_navigation_keyboard(0, len(questions))
        )
        
    except Exception as e:
        logger.error(f"Error starting profiler: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при запуске профайлера. Попробуйте позже.",
            reply_markup=get_profiler_keyboard()
        )


@router.message(ProfilerStates.answering_questions)
async def handle_answer(message: Message, state: FSMContext):
    """Handle user answer to profiling question"""
    try:
        data = await state.get_data()
        questions = data.get('questions', [])
        current_question = data.get('current_question', 0)
        answers = data.get('answers', [])
        
        # Save answer
        answer_text = message.text
        answers.append({
            'question_id': current_question,
            'question': questions[current_question]['question'],
            'answer': answer_text
        })
        
        # Move to next question
        next_question = current_question + 1
        
        if next_question < len(questions):
            # Update state
            await state.update_data(
                current_question=next_question,
                answers=answers
            )
            
            # Send next question
            question = questions[next_question]
            await message.answer(
                f"🔍 <b>Профайлинг партнера</b>\n\n"
                f"Вопрос {next_question + 1} из {len(questions)}:\n\n"
                f"<b>{question['question']}</b>\n\n"
                f"💡 {question['hint']}",
                parse_mode="HTML",
                reply_markup=get_profiler_navigation_keyboard(next_question, len(questions))
            )
        else:
            # All questions answered - start analysis
            await state.update_data(answers=answers)
            await start_analysis(message, state)
            
    except Exception as e:
        logger.error(f"Error handling answer: {e}")
        await message.answer(
            "❌ Произошла ошибка при обработке ответа. Попробуйте еще раз."
        )


async def start_analysis(message: Message, state: FSMContext):
    """Start AI analysis of answers"""
    try:
        # Get dependencies
        deps = get_dependencies()
        ai_service: AIService = deps['ai_service']
        html_pdf_service: HTMLPDFService = deps['html_pdf_service']
        user_service: UserService = deps['user_service']
        profile_service: ProfileService = deps['profile_service']
        
        # Get user data
        user_id = message.from_user.id
        data = await state.get_data()
        answers = data.get('answers', [])
        
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
        
        # Perform AI analysis
        try:
            analysis_result = await ai_service.profile_partner(answers, user_id)
            
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
                    questions=answers
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
        for block_key, score in block_scores.items():
            if block_key in block_names:
                scores_text += f"• {block_names[block_key]}: {score:.1f}/10\n"
        
        # Create summary message
        summary_text = (
            f"🔍 <b>АНАЛИЗ ЗАВЕРШЕН</b>\n\n"
            f"👤 <b>Партнер:</b> {partner_name}\n"
            f"{risk_emoji} <b>Уровень риска:</b> {overall_risk:.1f}% ({risk_level})\n\n"
            f"📊 <b>Детальные оценки:</b>\n{scores_text}\n"
            f"💭 <b>Заключение:</b> {risk_message}\n\n"
            f"📄 <b>Полный отчет прикреплен в формате PDF</b>\n"
            f"В отчете: детальный анализ, красные флаги, рекомендации по безопасности"
        )
        
        # Send PDF file
        pdf_file = BufferedInputFile(
            pdf_bytes,
            filename=f"partner_analysis_{partner_name}_{overall_risk:.0f}%.pdf"
        )
        
        await message.answer_document(
            document=pdf_file,
            caption=summary_text,
            parse_mode="HTML",
            reply_markup=get_profiler_keyboard()
        )
        
        # Send additional safety message for high risk cases
        if overall_risk >= 60:
            safety_text = (
                "⚠️ <b>ВАЖНО</b>\n\n"
                "Анализ выявил серьезные проблемы. Рекомендуется:\n"
                "• 🆘 Обратиться к психологу\n"
                "• 🛡️ Создать план безопасности\n"
                "• 📞 Сохранить номера экстренных служб\n"
                "• 👥 Поддерживать связь с близкими\n\n"
                "Помните: ваша безопасность важнее всего!"
            )
            await message.answer(safety_text, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error sending results: {e}")
        await message.answer(
            "✅ Анализ завершен, но возникла ошибка при отправке результатов. "
            "Попробуйте запросить анализ еще раз.",
            reply_markup=get_profiler_keyboard()
        )


@router.callback_query(F.data.startswith("profiler_nav_"))
async def handle_navigation(callback: CallbackQuery, state: FSMContext):
    """Handle navigation between questions"""
    try:
        await callback.answer()
        
        action = callback.data.split("_")[-1]
        data = await state.get_data()
        questions = data.get('questions', [])
        current_question = data.get('current_question', 0)
        
        if action == "back" and current_question > 0:
            new_question = current_question - 1
            await state.update_data(current_question=new_question)
            
            question = questions[new_question]
            await callback.message.edit_text(
                f"🔍 <b>Профайлинг партнера</b>\n\n"
                f"Вопрос {new_question + 1} из {len(questions)}:\n\n"
                f"<b>{question['question']}</b>\n\n"
                f"💡 {question['hint']}",
                parse_mode="HTML",
                reply_markup=get_profiler_navigation_keyboard(new_question, len(questions))
            )
        
        elif action == "skip":
            # Skip current question
            answers = data.get('answers', [])
            answers.append({
                'question_id': current_question,
                'question': questions[current_question]['question'],
                'answer': "Пропущено"
            })
            
            next_question = current_question + 1
            if next_question < len(questions):
                await state.update_data(
                    current_question=next_question,
                    answers=answers
                )
                
                question = questions[next_question]
                await callback.message.edit_text(
                    f"🔍 <b>Профайлинг партнера</b>\n\n"
                    f"Вопрос {next_question + 1} из {len(questions)}:\n\n"
                    f"<b>{question['question']}</b>\n\n"
                    f"💡 {question['hint']}",
                    parse_mode="HTML",
                    reply_markup=get_profiler_navigation_keyboard(next_question, len(questions))
                )
            else:
                # All questions done
                await state.update_data(answers=answers)
                await start_analysis(callback.message, state)
        
        elif action == "finish":
            # Finish early
            await start_analysis(callback.message, state)
            
    except Exception as e:
        logger.error(f"Error handling navigation: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка. Попробуйте еще раз.",
            reply_markup=get_profiler_keyboard()
        )


@router.callback_query(F.data == "profiler_back")
async def back_to_profiler(callback: CallbackQuery, state: FSMContext):
    """Return to profiler menu"""
    await callback.answer()
    await state.clear()
    
    await callback.message.edit_text(
        "🔍 <b>Профайлинг партнера</b>\n\n"
        "Выберите тип анализа:",
        parse_mode="HTML",
        reply_markup=get_profiler_keyboard()
    )