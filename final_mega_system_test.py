#!/usr/bin/env python3
"""
ФИНАЛЬНЫЙ ТЕСТ МЕГА-СИСТЕМЫ
Проверка полностью исправленной системы с добавлением risk_score
"""

import asyncio
import json
import time
from app.services.ai_service import ai_service

async def final_mega_system_test():
    """Финальный тест мега-системы с полной проверкой качества"""
    
    # Тестовые данные с высоким риском
    test_answers = [
        {
            "question": "Как партнер реагирует на ваши успехи?",
            "answer": "Михаил всегда находит способ принизить мои достижения. Когда я получила повышение, он сказал: 'Ну конечно, тебе просто повезло'. А когда я выиграла конкурс, он отозвался: 'Наверное, жюри просто пожалело тебя'.",
            "question_id": 1
        },
        {
            "question": "Проверяет ли он ваш телефон?",
            "answer": "Да, постоянно. Он говорит, что это нормально для пар, которые доверяют друг другу. Но если я отказываюсь показать телефон, он начинает кричать и обвинять меня в измене.",
            "question_id": 2
        },
        {
            "question": "Как он контролирует финансы?",
            "answer": "Он забрал мою карту и говорит, что будет сам распоряжаться деньгами. На каждую покупку нужно его разрешение. Даже за продукты не могу пойти одна - он дает точную сумму и требует чек.",
            "question_id": 3
        }
    ]
    
    print("🚀 ФИНАЛЬНЫЙ ТЕСТ МЕГА-СИСТЕМЫ")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # Запуск мега-системы
        result = await ai_service.profile_partner(
            answers=test_answers,
            user_id=100,
            partner_name="Михаил",
            partner_description="Контролирующий партнер",
            use_cache=False
        )
        
        processing_time = time.time() - start_time
        
        print(f"✅ МЕГА-СИСТЕМА УСПЕШНО ЗАВЕРШЕНА!")
        print(f"⏱️  Время обработки: {processing_time:.2f} сек ({processing_time/60:.1f} мин)")
        print(f"📊 Размер результата: {len(json.dumps(result, ensure_ascii=False))} символов")
        
        # Проверка ключевых показателей
        has_mega_metadata = "mega_metadata" in result
        has_risk_score = "risk_score" in result
        has_storytelling = "storytelling" in str(result) or "narrative" in str(result)
        has_expert_consensus = "expert_consensus" in str(result)
        has_comprehensive_recommendations = "comprehensive_recommendations" in result
        
        print(f"\n🔍 ПРОВЕРКА КАЧЕСТВА МЕГА-СИСТЕМЫ:")
        print(f"   ✓ Мега-метаданные: {'✅' if has_mega_metadata else '❌'}")
        print(f"   ✓ Оценка рисков: {'✅' if has_risk_score else '❌'}")
        print(f"   ✓ Storytelling: {'✅' if has_storytelling else '❌'}")
        print(f"   ✓ Экспертный консенсус: {'✅' if has_expert_consensus else '❌'}")
        print(f"   ✓ Комплексные рекомендации: {'✅' if has_comprehensive_recommendations else '❌'}")
        
        # Проверка мега-метаданных
        mega_meta = result.get("mega_metadata", {})
        if has_mega_metadata:
            print(f"\n🎯 МЕГА-МЕТАДАННЫЕ:")
            print(f"   🔢 Техник использовано: {mega_meta.get('techniques_used', 0)}/17")
            print(f"   📊 Уровней обработки: {mega_meta.get('processing_levels', 0)}/5")
            print(f"   🏆 Качество анализа: {mega_meta.get('quality_score', 0)}%")
            
            # Проверка полноты
            if mega_meta.get('techniques_used', 0) == 17 and mega_meta.get('processing_levels', 0) == 5:
                print(f"   ✅ ВСЕ ТЕХНИКИ И УРОВНИ АКТИВИРОВАНЫ!")
            else:
                print(f"   ⚠️  Не все компоненты активированы")
        
        # Проверка оценки рисков
        risk_score = result.get("risk_score", 0)
        if risk_score:
            print(f"\n⚠️  ОЦЕНКА РИСКОВ:")
            print(f"   📈 Общий риск: {risk_score}/100")
            
            if risk_score >= 80:
                print(f"   🔴 КРИТИЧЕСКИЙ РИСК - требуется немедленная помощь")
            elif risk_score >= 60:
                print(f"   🟡 ВЫСОКИЙ РИСК - требуется профессиональная помощь")
            elif risk_score >= 40:
                print(f"   🟠 СРЕДНИЙ РИСК - рекомендуется консультация")
            else:
                print(f"   🟢 НИЗКИЙ РИСК - профилактические меры")
        
        # Проверка детализации
        result_str = json.dumps(result, ensure_ascii=False)
        word_count = len(result_str.split())
        
        print(f"\n📝 ДЕТАЛИЗАЦИЯ АНАЛИЗА:")
        print(f"   📖 Количество слов: {word_count}")
        print(f"   📏 Детализация: {'Высокая' if word_count > 2000 else 'Средняя' if word_count > 1000 else 'Базовая'}")
        
        # Сохранение результата
        filename = f"mega_system_final_result_{int(time.time())}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Результат сохранен в {filename}")
        
        # Итоговая оценка
        quality_checks = [
            has_mega_metadata,
            has_risk_score,
            has_storytelling,
            has_expert_consensus,
            has_comprehensive_recommendations,
            mega_meta.get('techniques_used', 0) == 17,
            mega_meta.get('processing_levels', 0) == 5,
            risk_score > 0
        ]
        
        passed_checks = sum(quality_checks)
        total_checks = len(quality_checks)
        
        print(f"\n🎖️  ИТОГОВАЯ ОЦЕНКА: {passed_checks}/{total_checks} ({passed_checks/total_checks*100:.0f}%)")
        
        if passed_checks == total_checks:
            print(f"🏆 ОТЛИЧНО! Мега-система работает идеально!")
            return True
        elif passed_checks >= total_checks * 0.8:
            print(f"✅ ХОРОШО! Мега-система работает с небольшими недочетами")
            return True
        else:
            print(f"⚠️  УДОВЛЕТВОРИТЕЛЬНО. Есть проблемы, требующие внимания")
            return False
            
    except Exception as e:
        print(f"❌ ОШИБКА В МЕГА-СИСТЕМЕ: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(final_mega_system_test())
    if success:
        print("\n🎉 МЕГА-СИСТЕМА ГОТОВА К ПРОДАКШЕНУ!")
    else:
        print("\n🔧 Требуется дополнительная настройка") 