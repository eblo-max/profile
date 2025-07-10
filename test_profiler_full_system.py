#!/usr/bin/env python3
"""
Комплексное тестирование полной системы профайлера партнера
Тестирует: анкету, AI анализ, fallback режимы, систему безопасности, UI
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.prompts.profiler_full_questions import (
    get_all_questions, calculate_weighted_scores, get_safety_alerts,
    validate_full_answers, get_question_progress, get_next_question_state,
    QUESTION_ORDER
)
from app.prompts.profiler_full_prompts import (
    get_profiler_full_analysis_prompt, get_safety_assessment_prompt
)
from app.services.ai_service import ai_service


class ProfilerSystemTester:
    """Комплексный тестер системы профайлера"""
    
    def __init__(self):
        self.test_results = {
            "questions_system": False,
            "scoring_system": False,
            "safety_system": False,
            "ai_analysis": False,
            "fallback_system": False,
            "validation_system": False,
            "ui_components": False
        }
        self.errors = []
        
    def log(self, message: str, level: str = "INFO"):
        """Логирование с цветами"""
        colors = {
            "INFO": "\033[94m",  # Blue
            "SUCCESS": "\033[92m",  # Green  
            "ERROR": "\033[91m",  # Red
            "WARNING": "\033[93m",  # Yellow
            "RESET": "\033[0m"
        }
        
        print(f"{colors.get(level, '')}{level}: {message}{colors['RESET']}")
        
        if level == "ERROR":
            self.errors.append(message)

    def test_questions_system(self) -> bool:
        """Тест системы вопросов"""
        self.log("🔍 Тестирование системы вопросов...")
        
        try:
            # Test 1: Получение всех вопросов
            all_questions = get_all_questions()
            
            if len(all_questions) != 28:
                self.log(f"ОШИБКА: Ожидалось 28 вопросов, получено {len(all_questions)}", "ERROR")
                return False
            
            self.log(f"✅ Получено {len(all_questions)} вопросов", "SUCCESS")
            
            # Test 2: Проверка структуры вопросов
            required_fields = ['id', 'block', 'text', 'options', 'weight', 'context']
            
            for q_id, question in all_questions.items():
                for field in required_fields:
                    if field not in question:
                        self.log(f"ОШИБКА: Отсутствует поле '{field}' в вопросе {q_id}", "ERROR")
                        return False
                
                # Проверка количества опций
                if len(question['options']) != 5:
                    self.log(f"ОШИБКА: Ожидалось 5 опций в вопросе {q_id}, получено {len(question['options'])}", "ERROR")
                    return False
            
            self.log("✅ Структура всех вопросов корректна", "SUCCESS")
            
            # Test 3: Проверка порядка вопросов
            if len(QUESTION_ORDER) != 28:
                self.log(f"ОШИБКА: Неверный порядок вопросов, ожидалось 28, получено {len(QUESTION_ORDER)}", "ERROR")
                return False
            
            # Test 4: Проверка навигации
            for i, current_state in enumerate(QUESTION_ORDER):
                current_num, total = get_question_progress(current_state)
                
                if current_num != i + 1:
                    self.log(f"ОШИБКА: Неверный номер вопроса для {current_state}: {current_num} != {i + 1}", "ERROR")
                    return False
                
                if total != 28:
                    self.log(f"ОШИБКА: Неверное общее количество вопросов: {total} != 28", "ERROR")
                    return False
            
            self.log("✅ Навигация по вопросам работает корректно", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"ОШИБКА при тестировании вопросов: {e}", "ERROR")
            return False

    def generate_test_answers(self, risk_level: str = "medium") -> Dict[str, int]:
        """Генерация тестовых ответов для разных уровней риска"""
        all_questions = get_all_questions()
        answers = {}
        
        # Различные профили ответов
        risk_profiles = {
            "low": {
                "narcissism": 0,  # Низкие баллы нарциссизма
                "control": 1,     # Минимальный контроль
                "gaslighting": 0, # Без газлайтинга
                "emotion": 1,     # Хорошая регуляция эмоций
                "intimacy": 0,    # Уважение к границам
                "social": 1       # Здоровое социальное поведение
            },
            "medium": {
                "narcissism": 2,  
                "control": 2,     
                "gaslighting": 2, 
                "emotion": 2,     
                "intimacy": 2,    
                "social": 2       
            },
            "high": {
                "narcissism": 3,  
                "control": 3,     
                "gaslighting": 3, 
                "emotion": 3,     
                "intimacy": 3,    
                "social": 3       
            },
            "critical": {
                "narcissism": 4,  # Максимальные баллы риска
                "control": 4,     
                "gaslighting": 4, 
                "emotion": 4,     
                "intimacy": 4,    
                "social": 4       
            }
        }
        
        profile = risk_profiles.get(risk_level, risk_profiles["medium"])
        
        for q_id, question in all_questions.items():
            block = question['block']
            base_answer = profile.get(block, 2)
            
            # Добавляем небольшую случайность
            import random
            random_offset = random.randint(-1, 1) if base_answer > 0 and base_answer < 4 else 0
            final_answer = max(0, min(4, base_answer + random_offset))
            
            answers[q_id] = final_answer
        
        return answers

    def test_scoring_system(self) -> bool:
        """Тест системы подсчета баллов"""
        self.log("🔍 Тестирование системы скоринга...")
        
        try:
            # Тест на разных уровнях риска
            risk_levels = ["low", "medium", "high", "critical"]
            
            for risk_level in risk_levels:
                answers = self.generate_test_answers(risk_level)
                scores = calculate_weighted_scores(answers)
                
                # Проверка структуры результата
                required_keys = ["block_scores", "overall_risk_score", "urgency_level"]
                for key in required_keys:
                    if key not in scores:
                        self.log(f"ОШИБКА: Отсутствует ключ '{key}' в результатах скоринга", "ERROR")
                        return False
                
                # Проверка диапазонов
                overall_risk = scores["overall_risk_score"]
                if not (0 <= overall_risk <= 100):
                    self.log(f"ОШИБКА: Общий риск вне диапазона 0-100: {overall_risk}", "ERROR")
                    return False
                
                # Проверка блочных оценок
                block_scores = scores["block_scores"]
                expected_blocks = ["narcissism", "control", "gaslighting", "emotion", "intimacy", "social"]
                
                for block in expected_blocks:
                    if block not in block_scores:
                        self.log(f"ОШИБКА: Отсутствует блок '{block}' в оценках", "ERROR")
                        return False
                    
                    score = block_scores[block]
                    if not (0 <= score <= 10):
                        self.log(f"ОШИБКА: Оценка блока {block} вне диапазона 0-10: {score}", "ERROR")
                        return False
                
                self.log(f"✅ Скоринг для уровня '{risk_level}': {overall_risk:.1f}% риска", "SUCCESS")
            
            return True
            
        except Exception as e:
            self.log(f"ОШИБКА при тестировании скоринга: {e}", "ERROR")
            return False

    def test_safety_system(self) -> bool:
        """Тест системы безопасности"""
        self.log("🔍 Тестирование системы безопасности...")
        
        try:
            # Тест критического профиля
            critical_answers = self.generate_test_answers("critical")
            safety_alerts = get_safety_alerts(critical_answers)
            
            if not safety_alerts:
                self.log("ПРЕДУПРЕЖДЕНИЕ: Критический профиль не вызвал предупреждений безопасности", "WARNING")
            else:
                self.log(f"✅ Система безопасности обнаружила {len(safety_alerts)} предупреждений", "SUCCESS")
                for alert in safety_alerts[:3]:  # Показываем первые 3
                    self.log(f"   • {alert[:100]}...", "INFO")
            
            # Тест безопасного профиля
            safe_answers = self.generate_test_answers("low")
            safe_alerts = get_safety_alerts(safe_answers)
            
            if len(safe_alerts) > 2:  # Для низкого риска не должно быть много предупреждений
                self.log(f"ПРЕДУПРЕЖДЕНИЕ: Безопасный профиль вызвал {len(safe_alerts)} предупреждений", "WARNING")
            else:
                self.log("✅ Безопасный профиль корректно оценен", "SUCCESS")
            
            return True
            
        except Exception as e:
            self.log(f"ОШИБКА при тестировании системы безопасности: {e}", "ERROR")
            return False

    def test_validation_system(self) -> bool:
        """Тест системы валидации"""
        self.log("🔍 Тестирование системы валидации...")
        
        try:
            # Тест 1: Валидация полного набора ответов
            complete_answers = self.generate_test_answers("medium")
            is_valid, error_msg = validate_full_answers(complete_answers)
            
            if not is_valid:
                self.log(f"ОШИБКА: Полный набор ответов не прошел валидацию: {error_msg}", "ERROR")
                return False
            
            self.log("✅ Валидация полного набора ответов прошла успешно", "SUCCESS")
            
            # Тест 2: Валидация неполного набора
            incomplete_answers = dict(list(complete_answers.items())[:10])  # Только первые 10 ответов
            is_valid, error_msg = validate_full_answers(incomplete_answers)
            
            if is_valid:
                self.log("ОШИБКА: Неполный набор ответов прошел валидацию", "ERROR")
                return False
            
            self.log("✅ Валидация корректно отклонила неполный набор ответов", "SUCCESS")
            
            # Тест 3: Валидация с невалидными значениями
            invalid_answers = complete_answers.copy()
            invalid_answers["narcissism_q1"] = 10  # Значение вне диапазона 0-4
            
            is_valid, error_msg = validate_full_answers(invalid_answers)
            
            if is_valid:
                self.log("ОШИБКА: Набор с невалидными значениями прошел валидацию", "ERROR")
                return False
            
            self.log("✅ Валидация корректно отклонила невалидные значения", "SUCCESS")
            
            return True
            
        except Exception as e:
            self.log(f"ОШИБКА при тестировании валидации: {e}", "ERROR")
            return False

    async def test_ai_analysis(self) -> bool:
        """Тест AI анализа"""
        self.log("🔍 Тестирование AI анализа...")
        
        try:
            # Генерация тестовых данных
            test_answers = self.generate_test_answers("high")
            scores = calculate_weighted_scores(test_answers)
            
            # Тест AI анализа
            result = await ai_service.profile_partner(
                answers=test_answers,
                user_id=1,  # Тестовый ID
                partner_name="Тестовый партнер",
                partner_description="Тестовое описание для проверки AI анализа"
            )
            
            # Проверка структуры результата
            required_keys = [
                "overall_risk_score", "urgency_level", "block_scores",
                "analysis", "immediate_recommendations"
            ]
            
            for key in required_keys:
                if key not in result:
                    self.log(f"ОШИБКА: Отсутствует ключ '{key}' в результате AI анализа", "ERROR")
                    return False
            
            # Проверка качества анализа
            analysis_text = result.get("analysis", "")
            if len(analysis_text) < 100:
                self.log("ПРЕДУПРЕЖДЕНИЕ: AI анализ слишком короткий", "WARNING")
            
            recommendations = result.get("immediate_recommendations", [])
            if not recommendations:
                self.log("ПРЕДУПРЕЖДЕНИЕ: AI не предоставил рекомендации", "WARNING")
            
            self.log("✅ AI анализ выполнен успешно", "SUCCESS")
            self.log(f"   Общий риск: {result['overall_risk_score']:.1f}%", "INFO")
            self.log(f"   Уровень срочности: {result['urgency_level']}", "INFO")
            self.log(f"   Длина анализа: {len(analysis_text)} символов", "INFO")
            
            return True
            
        except Exception as e:
            self.log(f"ОШИБКА при тестировании AI анализа: {e}", "ERROR")
            return False

    async def test_fallback_system(self) -> bool:
        """Тест fallback системы"""
        self.log("🔍 Тестирование fallback системы...")
        
        try:
            # Создаем условия для fallback (отключаем AI)
            original_claude_key = ai_service.claude_client
            ai_service.claude_client = None  # Имитируем отсутствие AI
            
            test_answers = self.generate_test_answers("medium")
            
            # Попытка анализа без AI (должен использовать fallback)
            result = await ai_service.profile_partner(
                answers=test_answers,
                user_id=1,
                partner_name="Тестовый партнер (fallback)",
                partner_description=""
            )
            
            # Восстанавливаем AI клиент
            ai_service.claude_client = original_claude_key
            
            # Проверка, что fallback сработал
            if "analysis" not in result:
                self.log("ОШИБКА: Fallback система не предоставила анализ", "ERROR")
                return False
            
            if result["overall_risk_score"] == 0:
                self.log("ОШИБКА: Fallback система не рассчитала риск", "ERROR")
                return False
            
            self.log("✅ Fallback система работает корректно", "SUCCESS")
            self.log(f"   Fallback риск: {result['overall_risk_score']:.1f}%", "INFO")
            
            return True
            
        except Exception as e:
            self.log(f"ОШИБКА при тестировании fallback системы: {e}", "ERROR")
            return False

    def test_ui_components(self) -> bool:
        """Тест UI компонентов"""
        self.log("🔍 Тестирование UI компонентов...")
        
        try:
            # Проверка импортов клавиатур
            from app.bot.keyboards.inline import (
                profiler_full_navigation_kb, profiler_results_navigation_kb,
                profiler_block_analysis_kb, profiler_safety_plan_kb,
                profiler_my_profiles_kb, profiler_confirmation_kb,
                profiler_progress_visual_kb
            )
            
            # Тест создания клавиатур
            test_keyboards = [
                ("Navigation keyboard", profiler_full_navigation_kb, 
                 ("test_state", 5, 28, "Тестовый блок", False)),
                ("Results keyboard", profiler_results_navigation_kb, 
                 ("MEDIUM", False, 45.0)),
                ("Block analysis keyboard", profiler_block_analysis_kb, 
                 ({"narcissism": 5.0, "control": 6.0}, "")),
                ("Safety plan keyboard", profiler_safety_plan_kb, 
                 ("HIGH",)),
                ("My profiles keyboard", profiler_my_profiles_kb, 
                 (0,)),
                ("Confirmation keyboard", profiler_confirmation_kb, 
                 ("exit", "")),
                ("Progress visual keyboard", profiler_progress_visual_kb, 
                 (15, 28, {"narcissism_completed": 5, "narcissism_total": 7}))
            ]
            
            for name, func, args in test_keyboards:
                try:
                    keyboard = func(*args)
                    if not keyboard.inline_keyboard:
                        self.log(f"ОШИБКА: {name} пустая", "ERROR")
                        return False
                    self.log(f"✅ {name} создана успешно", "SUCCESS")
                except Exception as e:
                    self.log(f"ОШИБКА при создании {name}: {e}", "ERROR")
                    return False
            
            return True
            
        except Exception as e:
            self.log(f"ОШИБКА при тестировании UI: {e}", "ERROR")
            return False

    async def run_all_tests(self) -> Dict[str, Any]:
        """Запуск всех тестов"""
        self.log("🚀 Начинаем комплексное тестирование системы профайлера", "INFO")
        self.log("=" * 60, "INFO")
        
        # Синхронные тесты
        self.test_results["questions_system"] = self.test_questions_system()
        self.test_results["scoring_system"] = self.test_scoring_system()
        self.test_results["safety_system"] = self.test_safety_system()
        self.test_results["validation_system"] = self.test_validation_system()
        self.test_results["ui_components"] = self.test_ui_components()
        
        # Асинхронные тесты
        self.test_results["ai_analysis"] = await self.test_ai_analysis()
        self.test_results["fallback_system"] = await self.test_fallback_system()
        
        # Общий результат
        self.log("=" * 60, "INFO")
        self.log("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:", "INFO")
        
        all_passed = True
        for test_name, passed in self.test_results.items():
            status = "✅ ПРОЙДЕН" if passed else "❌ ПРОВАЛЕН"
            color = "SUCCESS" if passed else "ERROR"
            self.log(f"{test_name.replace('_', ' ').title()}: {status}", color)
            
            if not passed:
                all_passed = False
        
        self.log("=" * 60, "INFO")
        
        if all_passed:
            self.log("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!", "SUCCESS")
        else:
            self.log(f"⚠️  {len(self.errors)} ОШИБОК ОБНАРУЖЕНО:", "ERROR")
            for error in self.errors:
                self.log(f"   • {error}", "ERROR")
        
        return {
            "all_passed": all_passed,
            "test_results": self.test_results,
            "errors": self.errors,
            "total_tests": len(self.test_results),
            "passed_tests": sum(self.test_results.values())
        }


async def main():
    """Главная функция тестирования"""
    tester = ProfilerSystemTester()
    results = await tester.run_all_tests()
    
    # Сохранение результатов
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Результаты сохранены в test_results.json")
    
    # Возврат кода выхода
    return 0 if results["all_passed"] else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 