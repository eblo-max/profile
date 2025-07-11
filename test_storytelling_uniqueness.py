#!/usr/bin/env python3
"""
Тест уникальности контента и storytelling техники
Проверяет, что AI генерирует уникальный контент для каждого пользователя
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

from app.services.ai_service import AIService
from app.services.html_pdf_service import HTMLPDFService

class StorytellingUniquenessTest:
    """Тест уникальности контента и storytelling техники"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.pdf_service = HTMLPDFService()
        self.test_results = {}
        
    def create_test_scenarios(self):
        """Создает разные тестовые сценарии для проверки уникальности"""
        
        # Сценарий 1: Высокий риск - контролирующий нарцисс
        scenario1 = {
            "name": "Контролирующий нарцисс",
            "partner_name": "Александр Петров",
            "description": "Успешный бизнесмен, 35 лет",
            "answers": [
                {"question": "Контроль финансов", "answer": "Да, он контролирует все мои деньги, не даёт мне самостоятельно покупать даже мелочи"},
                {"question": "Критика внешности", "answer": "Да, он постоянно критикует мой вес, говорит что я толстая и непривлекательная"},
                {"question": "Изоляция от друзей", "answer": "Да, он запретил мне общаться с подругами, говорит что они плохо на меня влияют"},
                {"question": "Эмоциональный шантаж", "answer": "Да, он угрожает уйти к другой, если я не буду его слушаться"},
                {"question": "Контроль времени", "answer": "Да, он требует отчёт за каждую минуту, звонит каждые полчаса"},
                {"question": "Унижение публично", "answer": "Да, он может накричать на меня при других людях, унизить при детях"},
                {"question": "Ревность", "answer": "Да, он ревнует меня ко всем мужчинам, включая коллег и родственников"},
                {"question": "Газлайтинг", "answer": "Да, он говорит что я всё выдумываю, что у меня проблемы с памятью"},
                {"question": "Физическая агрессия", "answer": "Да, он может толкнуть, схватить за руку, бросить предмет"},
                {"question": "Контроль связи", "answer": "Да, он проверяет мой телефон, читает переписки, требует пароли от всех аккаунтов"}
            ]
        }
        
        # Сценарий 2: Средний риск - эмоционально нестабильный
        scenario2 = {
            "name": "Эмоционально нестабильный",
            "partner_name": "Дмитрий Сидоров", 
            "description": "Творческая личность, 28 лет",
            "answers": [
                {"question": "Контроль финансов", "answer": "Иногда, он хочет знать на что я трачу деньги"},
                {"question": "Критика внешности", "answer": "Иногда делает колкие замечания о моей одежде"},
                {"question": "Изоляция от друзей", "answer": "Не запрещает, но не любит когда я встречаюсь с подругами"},
                {"question": "Эмоциональный шантаж", "answer": "Да, он может угрожать расстаться в пылу ссоры"},
                {"question": "Контроль времени", "answer": "Нет, но расстраивается если я долго не отвечаю"},
                {"question": "Унижение публично", "answer": "Иногда может повысить голос при других"},
                {"question": "Ревность", "answer": "Да, он очень ревнивый, но пытается это скрывать"},
                {"question": "Газлайтинг", "answer": "Иногда говорит что я преувеличиваю"},
                {"question": "Физическая агрессия", "answer": "Нет, но может хлопнуть дверью или ударить по столу"},
                {"question": "Контроль связи", "answer": "Нет, но любит заглядывать в мой телефон"}
            ]
        }
        
        # Сценарий 3: Низкий риск - здоровые отношения
        scenario3 = {
            "name": "Здоровые отношения",
            "partner_name": "Максим Лебедев",
            "description": "Психолог, 32 года",
            "answers": [
                {"question": "Контроль финансов", "answer": "Нет, мы обсуждаем крупные покупки, но каждый тратит как хочет"},
                {"question": "Критика внешности", "answer": "Нет, он всегда говорит комплименты и поддерживает меня"},
                {"question": "Изоляция от друзей", "answer": "Нет, он поощряет мои дружеские отношения"},
                {"question": "Эмоциональный шантаж", "answer": "Нет, мы решаем конфликты через открытый диалог"},
                {"question": "Контроль времени", "answer": "Нет, у каждого есть своё личное время"},
                {"question": "Унижение публично", "answer": "Нет, он всегда поддерживает меня в обществе"},
                {"question": "Ревность", "answer": "Нет, он доверяет мне и не проявляет ревность"},
                {"question": "Газлайтинг", "answer": "Нет, он всегда признаёт мои чувства валидными"},
                {"question": "Физическая агрессия", "answer": "Нет, никогда не было никаких проявлений агрессии"},
                {"question": "Контроль связи", "answer": "Нет, у нас полная приватность в личных вещах"}
            ]
        }
        
        return [scenario1, scenario2, scenario3]
    
    async def test_storytelling_technique(self, scenario):
        """Тестирует использование storytelling техники"""
        print(f"\n🎭 Тестирую storytelling для: {scenario['name']}")
        
        try:
            # Генерируем анализ с использованием storytelling техники
            analysis = await self.ai_service.profile_partner_advanced(
                answers=scenario["answers"],
                user_id=999,
                partner_name=scenario["partner_name"],
                partner_description=scenario["description"],
                technique="storytelling",  # ИСПОЛЬЗУЕМ НОВУЮ ТЕХНИКУ!
                use_cache=False
            )
            
            # Проверяем структуру ответа
            psychological_profile = analysis.get("psychological_profile", "")
            
            # Анализируем качество storytelling
            storytelling_quality = self._analyze_storytelling_quality(
                psychological_profile, 
                scenario["partner_name"]
            )
            
            print(f"✅ Анализ сгенерирован для {scenario['partner_name']}")
            print(f"📊 Размер анализа: {len(psychological_profile)} символов")
            print(f"🎯 Качество storytelling: {storytelling_quality['score']}/10")
            
            return {
                "scenario": scenario["name"],
                "analysis": analysis,
                "storytelling_quality": storytelling_quality,
                "profile_text": psychological_profile
            }
            
        except Exception as e:
            print(f"❌ Ошибка при тестировании {scenario['name']}: {e}")
            return None
    
    def _analyze_storytelling_quality(self, text: str, partner_name: str) -> dict:
        """Анализирует качество storytelling в тексте"""
        
        quality_score = 0
        max_score = 10
        details = []
        
        # 1. Проверяем наличие имени партнера (1 балл)
        if partner_name in text:
            quality_score += 1
            details.append("✅ Имя партнера используется")
        else:
            details.append("❌ Имя партнера не используется")
            
        # 2. Проверяем наличие диалогов (2 балла)
        dialogue_markers = ['"', '«', '»', "говорит:", "сказал:", "отвечает:"]
        dialogue_found = any(marker in text for marker in dialogue_markers)
        if dialogue_found:
            quality_score += 2
            details.append("✅ Найдены диалоги")
        else:
            details.append("❌ Диалоги не найдены")
            
        # 3. Проверяем наличие конкретных сценариев (2 балла)
        scenario_markers = ["когда", "например", "представьте", "ситуация", "случай"]
        scenario_count = sum(1 for marker in scenario_markers if marker in text.lower())
        if scenario_count >= 3:
            quality_score += 2
            details.append(f"✅ Найдены сценарии: {scenario_count}")
        else:
            details.append(f"❌ Мало сценариев: {scenario_count}")
            
        # 4. Проверяем эмоциональную детализацию (2 балла)
        emotion_markers = ["чувствует", "испытывает", "переживает", "боится", "злится", "радуется"]
        emotion_count = sum(1 for marker in emotion_markers if marker in text.lower())
        if emotion_count >= 5:
            quality_score += 2
            details.append(f"✅ Эмоциональная детализация: {emotion_count}")
        else:
            details.append(f"❌ Мало эмоций: {emotion_count}")
            
        # 5. Проверяем живость повествования (1 балл)
        vivid_markers = ["постепенно", "медленно", "неожиданно", "вдруг", "затем"]
        vivid_count = sum(1 for marker in vivid_markers if marker in text.lower())
        if vivid_count >= 2:
            quality_score += 1
            details.append(f"✅ Живое повествование: {vivid_count}")
        else:
            details.append(f"❌ Статичное повествование: {vivid_count}")
            
        # 6. Проверяем длину и детализацию (2 балла)
        word_count = len(text.split())
        if word_count >= 800:
            quality_score += 2
            details.append(f"✅ Детальный анализ: {word_count} слов")
        elif word_count >= 400:
            quality_score += 1
            details.append(f"⚠️ Средний анализ: {word_count} слов")
        else:
            details.append(f"❌ Краткий анализ: {word_count} слов")
            
        return {
            "score": quality_score,
            "max_score": max_score,
            "percentage": (quality_score / max_score) * 100,
            "details": details
        }
    
    def _analyze_uniqueness(self, results: list) -> dict:
        """Анализирует уникальность контента между разными профилями"""
        
        print("\n🔍 Анализирую уникальность контента...")
        
        profiles = [result["profile_text"] for result in results if result]
        
        # Проверяем совпадения между профилями
        uniqueness_score = 0
        max_score = 100
        
        # 1. Проверяем использование разных имен
        names_used = set()
        for result in results:
            if result and result.get("scenario"):
                # Извлекаем имя партнера из сценария
                scenario_name = result["scenario"]
                names_used.add(scenario_name)
        
        if len(names_used) == len(results):
            uniqueness_score += 20
            print("✅ Все имена уникальны")
        else:
            print("❌ Имена повторяются")
            
        # 2. Проверяем различия в содержании
        if len(profiles) >= 2:
            # Простая проверка на совпадения
            for i, profile1 in enumerate(profiles):
                for j, profile2 in enumerate(profiles[i+1:], i+1):
                    # Разбиваем на предложения
                    sentences1 = set(profile1.split('.'))
                    sentences2 = set(profile2.split('.'))
                    
                    # Вычисляем пересечение
                    common_sentences = sentences1.intersection(sentences2)
                    total_sentences = len(sentences1.union(sentences2))
                    
                    if total_sentences > 0:
                        similarity = len(common_sentences) / total_sentences
                        uniqueness_score += max(0, 30 - (similarity * 100))
                        
                        print(f"📊 Сходство профилей {i+1} и {j+1}: {similarity:.1%}")
                        
        # 3. Проверяем различия в storytelling качестве
        storytelling_scores = [result["storytelling_quality"]["score"] for result in results if result]
        if len(set(storytelling_scores)) > 1:
            uniqueness_score += 25
            print("✅ Различное качество storytelling")
        else:
            print("❌ Одинаковое качество storytelling")
            
        # 4. Проверяем использование разных техник
        different_techniques = True
        for result in results:
            if result and "статичный шаблон" in result["profile_text"].lower():
                different_techniques = False
                break
                
        if different_techniques:
            uniqueness_score += 25
            print("✅ Используются динамические техники")
        else:
            print("❌ Используются статичные шаблоны")
            
        return {
            "uniqueness_score": uniqueness_score,
            "max_score": max_score,
            "percentage": (uniqueness_score / max_score) * 100,
            "profiles_count": len(profiles)
        }
    
    async def test_pdf_generation(self, analysis, partner_name):
        """Тестирует генерацию PDF с уникальным контентом"""
        print(f"\n📄 Генерирую PDF для {partner_name}...")
        
        try:
            pdf_bytes = await self.pdf_service.generate_partner_report_html(
                analysis_data=analysis,
                user_id=999,
                partner_name=partner_name
            )
            
            # Сохраняем PDF
            safe_name = partner_name.replace(" ", "_").replace(".", "")
            pdf_path = f"storytelling_test_{safe_name}.pdf"
            
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)
                
            print(f"✅ PDF сгенерирован: {pdf_path}")
            print(f"📊 Размер: {len(pdf_bytes)} байт ({len(pdf_bytes)/1024:.1f} KB)")
            
            return {
                "pdf_path": pdf_path,
                "pdf_size": len(pdf_bytes),
                "success": True
            }
            
        except Exception as e:
            print(f"❌ Ошибка генерации PDF: {e}")
            return {
                "pdf_path": None,
                "pdf_size": 0,
                "success": False,
                "error": str(e)
            }
    
    async def run_complete_uniqueness_test(self):
        """Запускает полный тест уникальности и storytelling"""
        print("🚀 ЗАПУСК ПОЛНОГО ТЕСТА УНИКАЛЬНОСТИ И STORYTELLING")
        print("=" * 70)
        
        start_time = datetime.now()
        
        # Создаем тестовые сценарии
        scenarios = self.create_test_scenarios()
        
        # Тестируем каждый сценарий
        results = []
        for scenario in scenarios:
            result = await self.test_storytelling_technique(scenario)
            if result:
                results.append(result)
                
        # Анализируем уникальность
        uniqueness_report = self._analyze_uniqueness(results)
        
        # Генерируем PDF для каждого результата
        pdf_results = []
        for result in results:
            if result:
                pdf_result = await self.test_pdf_generation(
                    result["analysis"],
                    result["analysis"].get("partner_name", "Test")
                )
                pdf_results.append(pdf_result)
        
        # Общий отчет
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Вычисляем общий балл
        avg_storytelling = sum(r["storytelling_quality"]["score"] for r in results) / len(results)
        uniqueness_score = uniqueness_report["percentage"]
        pdf_success_rate = sum(1 for r in pdf_results if r["success"]) / len(pdf_results) * 100
        
        overall_score = (avg_storytelling * 10 + uniqueness_score + pdf_success_rate) / 3
        
        # Сохраняем результаты
        self.test_results = {
            "timestamp": start_time.isoformat(),
            "duration_seconds": duration,
            "scenarios_tested": len(scenarios),
            "successful_analyses": len(results),
            "average_storytelling_score": avg_storytelling,
            "uniqueness_report": uniqueness_report,
            "pdf_results": pdf_results,
            "overall_score": overall_score,
            "grade": self._get_grade(overall_score)
        }
        
        # Сохраняем в файл
        with open("storytelling_uniqueness_test_results.json", "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        # Выводим итоговый отчет
        print("\n" + "=" * 70)
        print("🎉 ТЕСТ УНИКАЛЬНОСТИ И STORYTELLING ЗАВЕРШЕН!")
        print(f"⏱️ Время выполнения: {duration:.1f} секунд")
        print(f"📊 Протестировано сценариев: {len(scenarios)}")
        print(f"✅ Успешных анализов: {len(results)}")
        print(f"🎭 Среднее качество storytelling: {avg_storytelling:.1f}/10")
        print(f"🔍 Уникальность контента: {uniqueness_score:.1f}%")
        print(f"📄 PDF генерация: {pdf_success_rate:.1f}%")
        print(f"🎯 ОБЩИЙ БАЛЛ: {overall_score:.1f}/100 ({self._get_grade(overall_score)})")
        
        # Детальный вывод по каждому сценарию
        print("\n📋 ДЕТАЛЬНЫЙ ОТЧЕТ ПО СЦЕНАРИЯМ:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['scenario']}:")
            print(f"   🎭 Storytelling: {result['storytelling_quality']['score']}/10")
            print(f"   📝 Размер: {len(result['profile_text'])} символов")
            
            # Показываем первые 200 символов
            preview = result['profile_text'][:200] + "..." if len(result['profile_text']) > 200 else result['profile_text']
            print(f"   📖 Превью: {preview}")
            
        print(f"\n💾 Результаты сохранены в: storytelling_uniqueness_test_results.json")
        
        # Показываем созданные файлы
        print(f"\n📁 Созданные PDF файлы:")
        for pdf_result in pdf_results:
            if pdf_result["success"]:
                print(f"   ✅ {pdf_result['pdf_path']}")
            else:
                print(f"   ❌ Ошибка: {pdf_result.get('error', 'Unknown error')}")
        
        return self.test_results
    
    def _get_grade(self, score: float) -> str:
        """Получает оценку по баллам"""
        if score >= 90:
            return "A+ (Отлично)"
        elif score >= 80:
            return "A (Очень хорошо)"
        elif score >= 70:
            return "B (Хорошо)"
        elif score >= 60:
            return "C (Удовлетворительно)"
        else:
            return "D (Неудовлетворительно)"

# Функция для запуска теста
async def main():
    """Запускает тест уникальности и storytelling"""
    test = StorytellingUniquenessTest()
    await test.run_complete_uniqueness_test()

if __name__ == "__main__":
    asyncio.run(main()) 