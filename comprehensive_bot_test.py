#!/usr/bin/env python3
"""
Комплексный тест всего бота PsychoDetective
Проверяет все основные функции от начала до конца
"""

import asyncio
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List

# Настройка окружения
os.environ["TESTING"] = "true"
os.environ["LOG_LEVEL"] = "INFO"

# Импорты
from app.core.config import settings
from app.core.database import init_db
from app.services.ai_service import AIService  
from app.services.html_pdf_service import HTMLPDFService
from app.services.profile_service import ProfileService
from app.services.user_service import UserService
from app.models.user import User
from app.utils.enums import AnalysisType
from loguru import logger

class BotTester:
    """Класс для комплексного тестирования бота"""
    
    def __init__(self):
        self.test_user_id = 99999
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "overall_success": False,
            "errors": [],
            "performance": {}
        }
        self.services = {}
        
    async def initialize_services(self):
        """Инициализация всех сервисов"""
        print("🔧 ИНИЦИАЛИЗАЦИЯ СЕРВИСОВ")
        print("=" * 50)
        
        try:
            # Инициализация базы данных
            print("📦 Инициализация базы данных...")
            await init_db()
            print("✅ База данных готова")
            
            # Получение фабрики сессий
            from app.core.database import AsyncSessionLocal
            self.session_factory = AsyncSessionLocal
            print("🔗 Фабрика сессий создана")
            
            # Инициализация сервисов без сессии (будем создавать для каждого теста)
            print("🤖 Инициализация AI сервиса...")
            self.services['ai'] = AIService()
            print("✅ AI сервис готов")
            
            print("📄 Инициализация HTML/PDF сервиса...")
            self.services['html_pdf'] = HTMLPDFService()
            print("✅ HTML/PDF сервис готов")
            
            self.test_results["tests"]["service_initialization"] = {
                "success": True,
                "message": "Все сервисы инициализированы успешно"
            }
            
        except Exception as e:
            error_msg = f"Ошибка инициализации сервисов: {e}"
            print(f"❌ {error_msg}")
            self.test_results["tests"]["service_initialization"] = {
                "success": False,
                "error": error_msg
            }
            self.test_results["errors"].append(error_msg)
            
    async def test_user_management(self):
        """Тест управления пользователями"""
        print("\n👤 ТЕСТ УПРАВЛЕНИЯ ПОЛЬЗОВАТЕЛЯМИ")
        print("=" * 50)
        
        try:
            async with self.session_factory() as session:
                user_service = UserService(session)
                
                # Создание тестового пользователя
                print("🔧 Создание тестового пользователя...")
                user = await user_service.get_or_create_user(
                    telegram_id=self.test_user_id,
                    username="test_user",
                    first_name="Тест",
                    last_name="Пользователь"
                )
                print("✅ Пользователь создан")
                
                # Получение пользователя
                print("📋 Получение данных пользователя...")
                user = await user_service.get_user_by_telegram_id(self.test_user_id)
                if user:
                    print(f"✅ Пользователь найден: {user.first_name} {user.last_name}")
                else:
                    raise Exception("Пользователь не найден")
                
            self.test_results["tests"]["user_management"] = {
                "success": True,
                "message": "Управление пользователями работает"
            }
            
        except Exception as e:
            error_msg = f"Ошибка управления пользователями: {e}"
            print(f"❌ {error_msg}")
            self.test_results["tests"]["user_management"] = {
                "success": False,
                "error": error_msg
            }
            self.test_results["errors"].append(error_msg)
            
    async def test_text_analysis(self):
        """Тест анализа текста"""
        print("\n📝 ТЕСТ АНАЛИЗА ТЕКСТА")
        print("=" * 50)
        
        try:
            # Тестовая переписка
            test_text = """
            Он: Опять со своими подругами встречаешься? Сколько раз говорил - они тебя против меня настраивают!
            Я: Мы просто пили кофе...
            Он: "Просто пили кофе"... А о чем болтали? Наверняка обо мне! Они завидуют нашим отношениям!
            Я: Не завидуют, мы говорили о работе...
            Он: Не ври мне! Я все вижу! Если еще раз встретишься с ними без моего разрешения - пожалеешь!
            """
            
            print("🤖 Анализ тестовой переписки...")
            start_time = time.time()
            
            analysis = await self.services['ai'].analyze_text_advanced(
                text=test_text,
                user_id=self.test_user_id,
                context="переписка с партнером",
                technique="chain_of_thought"
            )
            
            analysis_time = time.time() - start_time
            
            print(f"✅ Анализ завершен за {analysis_time:.2f} сек")
            print(f"📊 Токсичность: {analysis.get('toxicity_score', 0)}/10")
            print(f"🚨 Уровень срочности: {analysis.get('urgency_level', 'UNKNOWN')}")
            print(f"🚩 Красные флаги найдены: {len(analysis.get('red_flags', []))}")
            
            self.test_results["tests"]["text_analysis"] = {
                "success": True,
                "message": "Анализ текста работает",
                "performance": {
                    "analysis_time": analysis_time,
                    "toxicity_score": analysis.get('toxicity_score', 0),
                    "red_flags_count": len(analysis.get('red_flags', []))
                }
            }
            
        except Exception as e:
            error_msg = f"Ошибка анализа текста: {e}"
            print(f"❌ {error_msg}")
            self.test_results["tests"]["text_analysis"] = {
                "success": False,
                "error": error_msg
            }
            self.test_results["errors"].append(error_msg)
            
    async def test_partner_profiling(self):
        """Тест профайлинга партнера"""
        print("\n🔍 ТЕСТ ПРОФАЙЛИНГА ПАРТНЕРА")
        print("=" * 50)
        
        try:
            # Тестовые ответы на вопросы
            test_answers = [
                {"question_id": "narcissism_q1", "question": "Как ваш партнер реагирует на критику?", "answer": "Агрессивно отвергает критику и обвиняет в ответ"},
                {"question_id": "narcissism_q2", "question": "Как партнер относится к чужим успехам?", "answer": "Злится и считает, что ему везет меньше"},
                {"question_id": "control_q1", "question": "Как партнер реагирует на ваши планы с друзьями?", "answer": "Категорически против, запрещает встречи"},
                {"question_id": "control_q2", "question": "Как партнер относится к вашим личным вещам?", "answer": "Постоянно контролирует все мои вещи и действия"},
                {"question_id": "gaslighting_q1", "question": "Как партнер ведет себя в спорах?", "answer": "Отрицает очевидные факты и заставляет сомневаться в себе"},
                {"question_id": "emotion_q1", "question": "Как партнер выражает гнев?", "answer": "Кричит, угрожает, может толкнуть или ударить"},
                {"question_id": "intimacy_q1", "question": "Как партнер относится к близости?", "answer": "Принуждает к близости, игнорирует отказы"},
                {"question_id": "social_q1", "question": "Как партнер ведет себя в обществе?", "answer": "Унижает меня при других, делает неприятные комментарии"}
            ]
            
            print("🤖 Анализ профиля партнера...")
            start_time = time.time()
            
            profile_analysis = await self.services['ai'].profile_partner_advanced(
                answers=test_answers,
                user_id=self.test_user_id,
                partner_name="Дмитрий Тестов",
                partner_description="Партнер с контролирующим поведением",
                technique="tree_of_thoughts"
            )
            
            analysis_time = time.time() - start_time
            
            print(f"✅ Профайлинг завершен за {analysis_time:.2f} сек")
            print(f"📊 Риск манипуляций: {profile_analysis.get('manipulation_risk', 0):.1f}/10")
            print(f"🚨 Уровень срочности: {profile_analysis.get('urgency_level', 'UNKNOWN')}")
            print(f"🚩 Красные флаги: {len(profile_analysis.get('red_flags', []))}")
            
            # Сохранение профиля
            print("💾 Сохранение профиля в базу данных...")
            async with self.session_factory() as session:
                profile_service = ProfileService(session)
                await profile_service.create_profile_from_profiler(
                    user_id=self.test_user_id,
                    partner_name="Дмитрий Тестов",
                    partner_description="Партнер с контролирующим поведением",
                    partner_basic_info="32 года, менеджер, встречаемся 2 года",
                    questions=test_answers,
                    answers={answer['question_id']: 4 for answer in test_answers},  # Высокий риск
                    analysis_result=profile_analysis
                )
            print("✅ Профиль сохранен")
            
            self.test_results["tests"]["partner_profiling"] = {
                "success": True,
                "message": "Профайлинг партнера работает",
                "performance": {
                    "analysis_time": analysis_time,
                    "manipulation_risk": profile_analysis.get('manipulation_risk', 0),
                    "red_flags_count": len(profile_analysis.get('red_flags', []))
                }
            }
            
        except Exception as e:
            error_msg = f"Ошибка профайлинга партнера: {e}"
            print(f"❌ {error_msg}")
            self.test_results["tests"]["partner_profiling"] = {
                "success": False,
                "error": error_msg
            }
            self.test_results["errors"].append(error_msg)
            
    async def test_pdf_generation(self):
        """Тест генерации PDF отчетов"""
        print("\n📄 ТЕСТ ГЕНЕРАЦИИ PDF ОТЧЕТОВ")
        print("=" * 50)
        
        try:
            # Тестовые данные для отчета
            test_analysis = {
                "psychological_profile": "Тестовый психологический профиль партнера с высоким уровнем контроля",
                "manipulation_risk": 8.5,
                "urgency_level": "HIGH",
                "red_flags": ["Контролирующее поведение", "Эмоциональное насилие", "Социальная изоляция"],
                "positive_traits": ["Умеет готовить", "Имеет работу"],
                "relationship_advice": "Рекомендуется осторожность и установление границ",
                "survival_guide": ["Создать план безопасности", "Обратиться за помощью"],
                "dark_triad": {"narcissism": 8.0, "machiavellianism": 7.5, "psychopathy": 6.0}
            }
            
            print("📄 Генерация HTML отчета...")
            start_time = time.time()
            
            pdf_bytes = await self.services['html_pdf'].generate_partner_report_html(
                analysis_data=test_analysis,
                user_id=self.test_user_id,
                partner_name="Дмитрий Тестов"
            )
            
            generation_time = time.time() - start_time
            
            if pdf_bytes and len(pdf_bytes) > 0:
                print(f"✅ PDF отчет сгенерирован за {generation_time:.2f} сек")
                print(f"📊 Размер файла: {len(pdf_bytes)} байт")
                
                # Сохранение тестового PDF
                with open("test_report.pdf", "wb") as f:
                    f.write(pdf_bytes)
                print("💾 Тестовый PDF сохранен как test_report.pdf")
                
            else:
                raise Exception("PDF не был сгенерирован")
            
            self.test_results["tests"]["pdf_generation"] = {
                "success": True,
                "message": "Генерация PDF работает",
                "performance": {
                    "generation_time": generation_time,
                    "file_size": len(pdf_bytes)
                }
            }
            
        except Exception as e:
            error_msg = f"Ошибка генерации PDF: {e}"
            print(f"❌ {error_msg}")
            self.test_results["tests"]["pdf_generation"] = {
                "success": False,
                "error": error_msg
            }
            self.test_results["errors"].append(error_msg)
            
    async def test_database_operations(self):
        """Тест операций с базой данных"""
        print("\n🗄️ ТЕСТ ОПЕРАЦИЙ С БАЗОЙ ДАННЫХ")
        print("=" * 50)
        
        try:
            async with self.session_factory() as session:
                profile_service = ProfileService(session)
                
                # Получение профилей пользователя
                print("📋 Получение профилей пользователя...")
                profiles = await profile_service.get_user_profiles(self.test_user_id)
                print(f"✅ Найдено профилей: {len(profiles)}")
                
                if profiles:
                    profile = profiles[0]
                    print(f"📊 Первый профиль: {profile.partner_name}, риск: {profile.manipulation_risk:.1f}/10")
                    
                    # Получение детальной информации о профиле
                    print("🔍 Получение детальной информации...")
                    detailed_profile = await profile_service.get_profile_by_id(profile.id, self.test_user_id)
                    if detailed_profile:
                        print("✅ Детальная информация получена")
                    else:
                        raise Exception("Не удалось получить детальную информацию")
            
            self.test_results["tests"]["database_operations"] = {
                "success": True,
                "message": "Операции с базой данных работают",
                "data": {
                    "profiles_count": len(profiles)
                }
            }
            
        except Exception as e:
            error_msg = f"Ошибка операций с БД: {e}"
            print(f"❌ {error_msg}")
            self.test_results["tests"]["database_operations"] = {
                "success": False,
                "error": error_msg
            }
            self.test_results["errors"].append(error_msg)
            
    async def test_bot_handlers(self):
        """Тест обработчиков бота (симуляция)"""
        print("\n🤖 ТЕСТ ОБРАБОТЧИКОВ БОТА")
        print("=" * 50)
        
        try:
            # Симуляция основных команд
            print("🔧 Симуляция обработчиков...")
            
            # Проверка промптов
            from app.prompts.profiler_full_questions import get_all_questions, QUESTION_ORDER
            questions = get_all_questions()
            print(f"📝 Загружено вопросов: {len(questions)}")
            print(f"📋 Порядок вопросов: {len(QUESTION_ORDER)}")
            
            # Проверка клавиатур
            from app.bot.keyboards.inline import profiler_menu_kb, get_profiler_question_keyboard
            menu_kb = profiler_menu_kb()
            print("⌨️ Клавиатуры загружены")
            
            # Создание тестовой клавиатуры
            test_keyboard = get_profiler_question_keyboard(
                "test_question",
                ["Вариант 1", "Вариант 2", "Вариант 3"]
            )
            print("✅ Тестовая клавиатура создана")
            
            self.test_results["tests"]["bot_handlers"] = {
                "success": True,
                "message": "Обработчики бота работают",
                "data": {
                    "questions_loaded": len(questions),
                    "question_order": len(QUESTION_ORDER)
                }
            }
            
        except Exception as e:
            error_msg = f"Ошибка обработчиков бота: {e}"
            print(f"❌ {error_msg}")
            self.test_results["tests"]["bot_handlers"] = {
                "success": False,
                "error": error_msg
            }
            self.test_results["errors"].append(error_msg)
            
    async def cleanup(self):
        """Очистка после тестов"""
        print("\n🧹 ОЧИСТКА ПОСЛЕ ТЕСТОВ")
        print("=" * 50)
        
        try:
            # Удаление тестовых данных
            print("🗑️ Удаление тестовых данных...")
            
            async with self.session_factory() as session:
                profile_service = ProfileService(session)
                
                # Удаление профилей
                profiles = await profile_service.get_user_profiles(self.test_user_id)
                for profile in profiles:
                    await profile_service.delete_profile(profile.id, self.test_user_id)
                print(f"✅ Удалено профилей: {len(profiles)}")
            
            # Удаление тестового PDF
            if os.path.exists("test_report.pdf"):
                os.remove("test_report.pdf")
                print("✅ Тестовый PDF удален")
            
            print("✅ Очистка завершена")
            
        except Exception as e:
            print(f"⚠️ Ошибка очистки: {e}")
            
    async def run_all_tests(self):
        """Запуск всех тестов"""
        print("🚀 ЗАПУСК КОМПЛЕКСНОГО ТЕСТА БОТА")
        print("=" * 80)
        print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 Тестовый пользователь: {self.test_user_id}")
        print("=" * 80)
        
        start_time = time.time()
        
        # Запуск всех тестов
        await self.initialize_services()
        await self.test_user_management()
        await self.test_text_analysis()
        await self.test_partner_profiling()
        await self.test_pdf_generation()
        await self.test_database_operations()
        await self.test_bot_handlers()
        await self.cleanup()
        
        total_time = time.time() - start_time
        
        # Подсчет результатов
        successful_tests = sum(1 for test in self.test_results["tests"].values() if test["success"])
        total_tests = len(self.test_results["tests"])
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        self.test_results["overall_success"] = success_rate == 100
        self.test_results["performance"]["total_time"] = total_time
        self.test_results["performance"]["success_rate"] = success_rate
        
        # Вывод итогов
        print("\n🎯 ИТОГИ ТЕСТИРОВАНИЯ")
        print("=" * 80)
        print(f"⏱️ Общее время: {total_time:.2f} сек")
        print(f"✅ Успешных тестов: {successful_tests}/{total_tests}")
        print(f"📊 Процент успеха: {success_rate:.1f}%")
        
        if self.test_results["overall_success"]:
            print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        else:
            print("❌ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ")
            print("\n🐛 Ошибки:")
            for error in self.test_results["errors"]:
                print(f"   • {error}")
        
        # Сохранение результатов
        with open("bot_test_results.json", "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Результаты сохранены в bot_test_results.json")
        
        return self.test_results["overall_success"]


async def main():
    """Главная функция"""
    tester = BotTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎊 БОТ ГОТОВ К ИСПОЛЬЗОВАНИЮ!")
        exit(0)
    else:
        print("\n⚠️ БОТ ТРЕБУЕТ ДОРАБОТКИ")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 