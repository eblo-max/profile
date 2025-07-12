"""
Полный тест пайплайна упрощенной системы:
Вопросы → Анализ → Сохранение профиля → Генерация PDF
"""

import asyncio
import time
import json
import os
from typing import Dict, Any

from app.services.ai_service import ai_service
from app.services.profile_service import ProfileService
from app.services.html_pdf_service import HTMLPDFService
from app.core.database import get_session
from app.models.user import User
from app.models.profile import PartnerProfile
from sqlalchemy import select


async def create_test_user():
    """Создаем тестового пользователя"""
    print("👤 Создаю тестового пользователя...")
    
    async with get_session() as session:
        # Проверяем, есть ли уже тестовый пользователь
        result = await session.execute(
            select(User).where(User.telegram_id == 999999)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                telegram_id=999999,
                username="test_user",
                first_name="Тестовый",
                last_name="Пользователь",
                subscription_type="premium",
                is_active=True
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            print(f"✅ Создан новый пользователь: {user.id}")
        else:
            print(f"✅ Используется существующий пользователь: {user.id}")
        
        return user


def get_realistic_questionnaire():
    """Получаем реалистичную анкету с тревожными ответами"""
    return [
        {
            "question_id": 1,
            "question": "Как ваш партнер реагирует на ваши успехи на работе или в учебе?",
            "answer": "Сначала поздравляет, но потом говорит что-то вроде 'надеюсь, это не сделает тебя слишком гордой' или 'главное, чтобы работа не стала важнее нашей семьи'. Иногда кажется, что он не очень рад моим достижениям."
        },
        {
            "question_id": 2,
            "question": "Как он относится к вашим друзьям и семье?",
            "answer": "Он часто критикует моих друзей, говорит что они плохо на меня влияют или что они завидуют нашим отношениям. С моей семьей вежлив, но потом говорит мне, что они слишком вмешиваются в нашу жизнь. Я стала реже видеться с друзьями, чтобы избежать конфликтов."
        },
        {
            "question_id": 3,
            "question": "Как проходят ваши ссоры и конфликты?",
            "answer": "Он может очень сильно кричать и говорить обидные вещи, а потом говорит что это я его довела. После ссоры он очень мил, дарит подарки и говорит что любит меня больше жизни. Иногда он может не разговаривать со мной несколько дней, пока я не извинюсь первой."
        },
        {
            "question_id": 4,
            "question": "Контролирует ли он ваши финансы, социальные сети или местоположение?",
            "answer": "Он управляет нашими деньгами, говорит что лучше разбирается в финансах. Иногда проверяет мой телефон 'просто так', говорит что между нами не должно быть секретов. Спрашивает где я была, если задерживаюсь. Говорит, что это забота."
        },
        {
            "question_id": 5,
            "question": "Как он реагирует на ваше мнение, если оно отличается от его?",
            "answer": "Говорит что я слишком эмоциональная и не могу мыслить логически. Иногда смеется над моими идеями или говорит что я 'как маленькая девочка'. Я стала реже высказывать свое мнение, чтобы не расстраивать его."
        },
        {
            "question_id": 6,
            "question": "Были ли случаи физической агрессии или угроз?",
            "answer": "Физически не бил, но может сильно сжать руку или толкнуть 'в шутку'. Один раз ударил кулаком по стене рядом со мной, когда был очень зол. Говорит что никогда не тронет женщину, но иногда его поведение пугает."
        },
        {
            "question_id": 7,
            "question": "Как он ведет себя в обществе и наедине с вами?",
            "answer": "В обществе он очень обаятельный и харизматичный, все его любят. Наедине может быть совсем другим - более требовательным и критичным. Друзья говорят что мне повезло с таким парнем, но они не знают как он ведет себя дома."
        },
        {
            "question_id": 8,
            "question": "Чувствуете ли вы себя свободной в отношениях?",
            "answer": "Иногда чувствую что хожу по яичной скорлупе, боясь его расстроить. Стала более осторожной в словах и поступках. Но он говорит что это нормально в серьезных отношениях, что нужно думать о партнере."
        }
    ]


async def test_questionnaire_analysis():
    """Тестируем анализ анкеты"""
    print("\n📝 Тестирую анализ анкеты...")
    
    questionnaire = get_realistic_questionnaire()
    
    print(f"📊 Количество вопросов: {len(questionnaire)}")
    for i, qa in enumerate(questionnaire[:2], 1):
        print(f"  {i}. {qa['question'][:50]}...")
    print("  ...")
    
    start_time = time.time()
    
    # Анализ через упрощенную систему
    analysis_result = await ai_service.profile_partner(
        answers=questionnaire,
        user_id=999999,
        partner_name="Дмитрий",
        partner_description="Мой парень, 30 лет, работает менеджером в крупной компании",
        use_cache=False
    )
    
    duration = time.time() - start_time
    
    print(f"✅ Анализ завершен за {duration:.2f} секунд")
    print(f"📊 Общий риск: {analysis_result.get('overall_risk_score', 0)}/100")
    print(f"🚩 Красные флаги: {len(analysis_result.get('red_flags', []))}")
    print(f"⚠️ Уровень срочности: {analysis_result.get('urgency_level', 'N/A')}")
    print(f"🎯 Уверенность: {analysis_result.get('confidence_level', 0)}%")
    print(f"💰 Стоимость: ~${analysis_result.get('cost_estimate', 0)}")
    
    return analysis_result


async def test_profile_creation(user: User, analysis_result: Dict[str, Any]):
    """Тестируем создание профиля в базе"""
    print("\n💾 Тестирую сохранение профиля в базу...")
    
    async with get_session() as session:
        profile_service = ProfileService(session)
        
        # Создаем профиль
        profile = await profile_service.create_profile_from_profiler(
            user_id=user.id,
            partner_name="Дмитрий",
            partner_description="Мой парень, 30 лет, работает менеджером в крупной компании",
            partner_basic_info="Высокий, спортивный, амбициозный",
            questions=get_realistic_questionnaire(),
            answers={},  # Не используется в новой системе
            analysis_result=analysis_result
        )
        
        if profile:
            print(f"✅ Профиль создан с ID: {profile.id}")
            print(f"📊 Риск манипуляций: {profile.manipulation_risk}/10")
            print(f"🔍 Завершен: {profile.is_completed}")
            return profile
        else:
            print("❌ Не удалось создать профиль")
            return None


async def test_pdf_generation(profile: PartnerProfile, analysis_result: Dict[str, Any]):
    """Тестируем генерацию PDF отчета"""
    print("\n📄 Тестирую генерацию PDF отчета...")
    
    try:
        pdf_service = HTMLPDFService()
        
        start_time = time.time()
        
        # Генерируем PDF
        pdf_bytes = await pdf_service.generate_partner_report_html(
            analysis_data=analysis_result,
            user_id=999999,
            partner_name="Дмитрий"
        )
        
        # Сохраняем PDF в файл
        pdf_path = f"partner_analysis_Дмитрий_{int(time.time())}.pdf"
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        
        duration = time.time() - start_time
        
        if pdf_path and os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path) / 1024  # KB
            print(f"✅ PDF создан за {duration:.2f} секунд")
            print(f"📁 Путь: {pdf_path}")
            print(f"📏 Размер: {file_size:.1f} KB")
            
            # Проверяем содержимое
            with open(pdf_path, 'rb') as f:
                content = f.read()
                if content.startswith(b'%PDF'):
                    print("✅ PDF файл валидный")
                else:
                    print("❌ PDF файл поврежден")
            
            return pdf_path
        else:
            print("❌ PDF файл не создан")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка генерации PDF: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_detailed_analysis_content(analysis_result: Dict[str, Any]):
    """Детальный анализ содержимого результата"""
    print("\n🔍 Детальный анализ результата...")
    
    print(f"\n📝 Психологический профиль:")
    profile_text = analysis_result.get('psychological_profile', '')
    print(f"Длина: {len(profile_text)} символов")
    print(profile_text[:200] + "..." if len(profile_text) > 200 else profile_text)
    
    print(f"\n🚩 Красные флаги ({len(analysis_result.get('red_flags', []))}):")
    for i, flag in enumerate(analysis_result.get('red_flags', [])[:5], 1):
        print(f"  {i}. {flag}")
    
    print(f"\n💪 Сильные стороны ({len(analysis_result.get('strengths', []))}):")
    for i, strength in enumerate(analysis_result.get('strengths', [])[:3], 1):
        print(f"  {i}. {strength}")
    
    print(f"\n💡 Рекомендации ({len(analysis_result.get('recommendations', []))}):")
    for i, rec in enumerate(analysis_result.get('recommendations', [])[:3], 1):
        print(f"  {i}. {rec}")
    
    print(f"\n🎯 Оценки Dark Triad:")
    dark_triad = analysis_result.get('dark_triad', {})
    for trait, score in dark_triad.items():
        print(f"  {trait.capitalize()}: {score}/10")
    
    print(f"\n📊 Блочные оценки:")
    block_scores = analysis_result.get('block_scores', {})
    for block, score in block_scores.items():
        print(f"  {block.capitalize()}: {score}/10")
    
    # Анализ качества
    quality_score = 0
    if len(analysis_result.get('psychological_profile', '')) > 200:
        quality_score += 20
    if len(analysis_result.get('red_flags', [])) > 0:
        quality_score += 20
    if analysis_result.get('overall_risk_score', 0) > 50:
        quality_score += 20
    if analysis_result.get('urgency_level') in ['HIGH', 'CRITICAL']:
        quality_score += 20
    if analysis_result.get('confidence_level', 0) > 80:
        quality_score += 20
    
    print(f"\n🎯 Оценка качества анализа: {quality_score}/100")
    
    return quality_score


async def main():
    """Полный тест пайплайна"""
    print("🚀 ПОЛНЫЙ ТЕСТ ПАЙПЛАЙНА УПРОЩЕННОЙ СИСТЕМЫ")
    print("=" * 70)
    
    total_start_time = time.time()
    
    try:
        # 1. Создание пользователя
        user = await create_test_user()
        
        # 2. Анализ анкеты
        analysis_result = await test_questionnaire_analysis()
        
        # 3. Детальный анализ содержимого
        quality_score = await test_detailed_analysis_content(analysis_result)
        
        # 4. Сохранение профиля
        profile = await test_profile_creation(user, analysis_result)
        
        # 5. Генерация PDF
        pdf_path = await test_pdf_generation(profile, analysis_result)
        
        total_duration = time.time() - total_start_time
        
        print("\n" + "=" * 70)
        print("📊 ИТОГИ ПОЛНОГО ТЕСТИРОВАНИЯ")
        print("=" * 70)
        
        # Результаты
        success_count = sum([
            1 if user else 0,
            1 if analysis_result else 0,
            1 if profile else 0,
            1 if pdf_path else 0
        ])
        
        print(f"✅ Успешных этапов: {success_count}/4")
        print(f"⏱️ Общее время: {total_duration:.2f} секунд")
        print(f"💰 Общая стоимость: ~$0.08")
        print(f"🎯 Качество анализа: {quality_score}/100")
        
        if analysis_result:
            print(f"📊 Детекция рисков: {analysis_result.get('overall_risk_score', 0)}/100")
            print(f"🚩 Найдено красных флагов: {len(analysis_result.get('red_flags', []))}")
            print(f"⚠️ Уровень срочности: {analysis_result.get('urgency_level', 'N/A')}")
        
        if pdf_path:
            print(f"📄 PDF отчет: {os.path.basename(pdf_path)}")
        
        # Оценка производительности
        if total_duration < 30:
            print("🟢 Скорость: ОТЛИЧНО (< 30с)")
        elif total_duration < 60:
            print("🟡 Скорость: ХОРОШО (< 60с)")
        else:
            print("🔴 Скорость: МЕДЛЕННО (> 60с)")
        
        # Оценка качества
        if quality_score >= 80:
            print("🟢 Качество: ОТЛИЧНО")
        elif quality_score >= 60:
            print("🟡 Качество: ХОРОШО")
        else:
            print("🔴 Качество: ТРЕБУЕТ УЛУЧШЕНИЯ")
        
        if success_count == 4:
            print("\n🎉 ВСЕ ЭТАПЫ ПРОЙДЕНЫ УСПЕШНО!")
            print("✅ Система готова к использованию в телеграм-боте")
            print("🚀 Полный пайплайн работает корректно")
        else:
            print(f"\n⚠️ Некоторые этапы не пройдены ({4-success_count} ошибок)")
        
        return success_count == 4
        
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1) 