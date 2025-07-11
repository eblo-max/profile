#!/usr/bin/env python3
"""
Отладочный скрипт для проверки первого этапа итеративного подхода
"""

import asyncio
import json
from app.services.ai_service import ai_service
from app.prompts.ultra_personalization_prompt import create_storytelling_analysis_prompt
from app.utils.helpers import extract_json_from_text, safe_json_loads

async def debug_first_stage():
    """Отладка первого этапа - получение структурированных данных"""
    
    try:
        # Тестовые данные
        test_answers = [
            {"question": "Как партнер реагирует на ваши успехи?", "answer": "Михаил всегда находит способ принизить мои достижения. Когда я получила повышение, он сказал: 'Ну конечно, тебе просто повезло'. А когда я выиграла конкурс, он отозвался: 'Наверное, жюри просто пожалело тебя'."},
            {"question": "Проверяет ли он ваш телефон?", "answer": "Да, постоянно. Он говорит, что это нормально для пар, которые доверяют друг другу. Но если я отказываюсь показать телефон, он начинает кричать и обвинять меня в измене."},
            {"question": "Как он контролирует финансы?", "answer": "Он забрал мою карту и говорит, что будет сам распоряжаться деньгами. На каждую покупку нужно его разрешение. Даже за продукты не могу пойти одна - он дает точную сумму и требует чек."},
            {"question": "Изолирует ли он вас от друзей?", "answer": "Постепенно я перестала видеться с друзьями. Михаил всегда находил повод не отпускать: то у него были планы, то мои подруги 'плохо на меня влияют'. Теперь я почти никого не вижу."},
            {"question": "Как он реагирует на критику?", "answer": "Очень агрессивно. Если я пытаюсь высказать недовольство, он кричит, что я неблагодарная, что все женщины одинаковые. Может несколько дней не разговаривать или уйти из дома."}
        ]
        
        print("🔍 ОТЛАДКА ПЕРВОГО ЭТАПА ИТЕРАТИВНОГО ПОДХОДА")
        print("=" * 60)
        
        # Формируем ответы как строку
        answers_text = "\n".join([f"Q: {q['question']}\nA: {q['answer']}" for q in test_answers])
        
        # Создаем промпт для первого этапа
        prompt = create_storytelling_analysis_prompt(
            answers_text=answers_text,
            partner_name="Михаил",
            partner_description="Партнер из анкеты"
        )
        
        print("📝 ПРОМПТ ПЕРВОГО ЭТАПА:")
        print("-" * 30)
        print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
        print("-" * 30)
        
        # Получаем ответ от AI
        print("\n📡 Запрос к AI...")
        response = await ai_service._get_ai_response(
            system_prompt="Ты - эксперт психолог. Проанализируй поведение партнера.",
            user_prompt=prompt,
            response_format="json",
            max_tokens=4000,
            technique="storytelling"
        )
        
        print("✅ Ответ получен!")
        print(f"📊 Длина ответа: {len(response)} символов")
        
        # Парсим JSON
        try:
            structured_data = extract_json_from_text(response)
            if not structured_data:
                structured_data = safe_json_loads(response, {})
            
            print("\n🏗️ СТРУКТУРИРОВАННЫЕ ДАННЫЕ:")
            print("-" * 40)
            print(json.dumps(structured_data, indent=2, ensure_ascii=False))
            print("-" * 40)
            
            # Анализируем данные
            print("\n📊 АНАЛИЗ СТРУКТУРИРОВАННЫХ ДАННЫХ:")
            print(f"   Тип личности: {structured_data.get('personality_type', 'N/A')[:100]}...")
            print(f"   Red flags: {len(structured_data.get('red_flags', []))}")
            print(f"   Персональные инсайты: {len(structured_data.get('personalized_insights', []))}")
            print(f"   Поведенческие доказательства: {len(structured_data.get('behavioral_evidence', []))}")
            print(f"   Риск манипуляций: {structured_data.get('manipulation_risk', 'N/A')}")
            print(f"   Уровень срочности: {structured_data.get('urgency_level', 'N/A')}")
            
            # Проверяем ключевые поля
            if structured_data.get('red_flags'):
                print("\n🚨 RED FLAGS:")
                for i, flag in enumerate(structured_data['red_flags'], 1):
                    print(f"   {i}. {flag}")
            
            if structured_data.get('personalized_insights'):
                print("\n💡 ПЕРСОНАЛЬНЫЕ ИНСАЙТЫ:")
                for i, insight in enumerate(structured_data['personalized_insights'], 1):
                    print(f"   {i}. {insight}")
            
            return structured_data
            
        except Exception as e:
            print(f"❌ ОШИБКА ПАРСИНГА JSON: {e}")
            print("🔍 СЫРОЙ ОТВЕТ:")
            print(response)
            return None
            
    except Exception as e:
        print(f"❌ ОБЩАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(debug_first_stage()) 