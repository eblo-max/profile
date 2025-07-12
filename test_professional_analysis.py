import asyncio
import random
import re
from app.services.ai_service import AIService
from app.core.config import settings
import time

def get_detailed_questionnaire():
    """Возвращает детальную анкету с конкретными ситуациями"""
    return {
        "q1": {
            "question": "Как ваш партнер реагирует на ваши профессиональные успехи?",
            "options": [
                "Искренне радуется и поддерживает меня",
                "Сначала поздравляет, но потом находит негативные стороны",
                "Переводит разговор на свои достижения",
                "Принижает важность моих успехов словами вроде 'это не так сложно'",
                "Обвиняет меня в том, что работа важнее отношений"
            ]
        },
        "q2": {
            "question": "Как он контролирует ваши финансы?",
            "options": [
                "Мы совместно планируем бюджет как равные партнеры",
                "Он дает советы, но решения принимаю я",
                "Настаивает на том, чтобы знать все мои траты",
                "Требует отчета за каждую покупку и чеки",
                "Держит все деньги у себя, я должна просить на расходы"
            ]
        },
        "q3": {
            "question": "Как он ведет себя во время конфликтов?",
            "options": [
                "Спокойно обсуждает проблему и ищет компромисс",
                "Повышает голос, но потом извиняется",
                "Кричит и обвиняет меня во всех проблемах",
                "Оскорбляет меня словами 'ты глупая', 'ты ничего не понимаешь'",
                "Может угрожать разрывом отношений или физической агрессией"
            ]
        },
        "q4": {
            "question": "Как он относится к вашим друзьям и семье?",
            "options": [
                "Хорошо ладит со всеми и поддерживает мои отношения",
                "Терпит их, но иногда делает критические замечания",
                "Постоянно находит недостатки в моих близких",
                "Говорит что они 'плохо на меня влияют' и 'настраивают против него'",
                "Запрещает или ограничивает общение с друзьями и семьей"
            ]
        },
        "q5": {
            "question": "Как он проверяет вашу переписку и социальные сети?",
            "options": [
                "Никогда не проверяет, полностью мне доверяет",
                "Иногда просит показать конкретное сообщение",
                "Регулярно просматривает мои сообщения и фото",
                "Требует пароли от всех аккаунтов 'у нас не должно быть секретов'",
                "Постоянно следит за моей активностью и требует объяснений"
            ]
        },
        "q6": {
            "question": "Как он реагирует на ваши просьбы о личном времени?",
            "options": [
                "Понимает и уважает мою потребность в одиночестве",
                "Соглашается, но может немного обижаться",
                "Воспринимает как отвержение и устраивает сцены",
                "Говорит 'если любишь, то хочешь быть со мной всегда'",
                "Преследует меня и не дает побыть одной"
            ]
        },
        "q7": {
            "question": "Как он ведет себя в обществе по сравнению с домом?",
            "options": [
                "Одинаково уважительно везде",
                "Немного более сдержанный на публике",
                "Кардинально меняется - мил с другими, груб со мной",
                "При людях изображает идеального мужа, дома становится агрессивным",
                "Может унижать меня даже при посторонних"
            ]
        },
        "q8": {
            "question": "Как он реагирует на критику с вашей стороны?",
            "options": [
                "Выслушивает и готов обсуждать проблемы",
                "Защищается, но может признать ошибки",
                "Агрессивно отвергает любые замечания",
                "Переворачивает ситуацию: 'это ты во всем виновата'",
                "Наказывает меня холодностью или угрозами за критику"
            ]
        },
        "q9": {
            "question": "Как он относится к вашему 'нет' в интимных вопросах?",
            "options": [
                "Уважает мои границы без вопросов",
                "Расстраивается, но принимает мое решение",
                "Обижается и говорит что я 'холодная' и 'не люблю его'",
                "Принуждает через фразы 'если любишь, то не откажешь'",
                "Игнорирует мой отказ и настаивает на своем"
            ]
        },
        "q10": {
            "question": "Как он использует информацию о ваших слабостях?",
            "options": [
                "Помогает мне справляться с трудностями",
                "Иногда может неосторожно затронуть болезненную тему",
                "Использует мои слабости в спорах против меня",
                "Целенаправленно давит на болевые точки во время ссор",
                "Угрожает рассказать другим мои секреты"
            ]
        }
    }

def generate_realistic_answers():
    """Генерирует реалистичные ответы с высокой токсичностью"""
    questionnaire = get_detailed_questionnaire()
    answers = []
    
    # Конкретные токсичные ответы для более реалистичного анализа
    toxic_answers = [
        "Переводит разговор на свои достижения",
        "Держит все деньги у себя, я должна просить на расходы", 
        "Оскорбляет меня словами 'ты глупая', 'ты ничего не понимаешь'",
        "Говорит что они 'плохо на меня влияют' и 'настраивают против него'",
        "Требует пароли от всех аккаунтов 'у нас не должно быть секретов'",
        "Говорит 'если любишь, то хочешь быть со мной всегда'",
        "При людях изображает идеального мужа, дома становится агрессивным",
        "Переворачивает ситуацию: 'это ты во всем виновата'",
        "Принуждает через фразы 'если любишь, то не откажешь'",
        "Целенаправленно давит на болевые точки во время ссор"
    ]
    
    for i, (q_id, q_data) in enumerate(questionnaire.items()):
        if i < len(toxic_answers):
            selected_answer = toxic_answers[i]
        else:
            # Для остальных вопросов выбираем случайный токсичный ответ
            weights = [0.05, 0.15, 0.25, 0.35, 0.20]  # Больше веса на токсичные варианты
            selected_index = random.choices(range(len(q_data["options"])), weights=weights)[0]
            selected_answer = q_data["options"][selected_index]
        
        answers.append({
            "question": q_data["question"],
            "answer": selected_answer,
            "question_id": q_id
        })
    
    return answers

def generate_partner_profile():
    """Генерирует детальный профиль партнера"""
    profiles = [
        {
            "name": "Дмитрий",
            "age": 32,
            "profession": "менеджер по продажам",
            "description": "Дмитрий, 32 года, работает менеджером по продажам в крупной компании"
        },
        {
            "name": "Алексей", 
            "age": 29,
            "profession": "предприниматель",
            "description": "Алексей, 29 лет, владелец небольшого бизнеса"
        },
        {
            "name": "Сергей",
            "age": 35,
            "profession": "IT-специалист",
            "description": "Сергей, 35 лет, работает программистом в IT-компании"
        }
    ]
    
    return random.choice(profiles)

def analyze_quality(result, partner_name):
    """Детальный анализ качества портрета"""
    profile_text = result.get('psychological_profile', '')
    word_count = len(profile_text.split())
    
    quality_score = 0
    max_score = 120
    
    print(f"\n📊 ДЕТАЛЬНЫЙ АНАЛИЗ КАЧЕСТВА:")
    print("=" * 60)
    
    # 1. Объем (25 баллов)
    print(f"1. ОБЪЕМ АНАЛИЗА:")
    print(f"   Слов: {word_count}")
    print(f"   Символов: {len(profile_text)}")
    
    if word_count >= 2200:
        quality_score += 25
        print(f"   ✅ ОТЛИЧНО: {word_count} слов (цель: 2200-2500)")
    elif word_count >= 1800:
        quality_score += 20
        print(f"   🟡 ХОРОШО: {word_count} слов (близко к цели)")
    elif word_count >= 1400:
        quality_score += 15
        print(f"   🟠 УДОВЛЕТВОРИТЕЛЬНО: {word_count} слов")
    else:
        quality_score += 5
        print(f"   🔴 НЕДОСТАТОЧНО: {word_count} слов")
    
    # 2. Персонализация - упоминание имени (20 баллов)
    name_mentions = profile_text.count(partner_name)
    print(f"\n2. ПЕРСОНАЛИЗАЦИЯ:")
    print(f"   Упоминаний имени '{partner_name}': {name_mentions}")
    
    if name_mentions >= 8:
        quality_score += 20
        print(f"   ✅ ОТЛИЧНО: {name_mentions} упоминаний (цель: 8-10)")
    elif name_mentions >= 5:
        quality_score += 15
        print(f"   🟡 ХОРОШО: {name_mentions} упоминаний")
    elif name_mentions >= 2:
        quality_score += 10
        print(f"   🟠 УДОВЛЕТВОРИТЕЛЬНО: {name_mentions} упоминаний")
    else:
        quality_score += 0
        print(f"   🔴 ПЛОХО: {name_mentions} упоминаний")
    
    # 3. Структура без смайликов (15 баллов)
    emoji_count = len(re.findall(r'[😀-🙿]|[🚀-🛿]|[☀-⛿]', profile_text))
    hash_count = profile_text.count('#')
    print(f"\n3. ПРОФЕССИОНАЛЬНАЯ СТРУКТУРА:")
    print(f"   Смайликов: {emoji_count}")
    print(f"   Решеток: {hash_count}")
    
    if emoji_count == 0 and hash_count == 0:
        quality_score += 15
        print(f"   ✅ ОТЛИЧНО: Чистый профессиональный текст")
    elif emoji_count <= 2 and hash_count <= 2:
        quality_score += 10
        print(f"   🟡 ХОРОШО: Минимум лишних символов")
    else:
        quality_score += 5
        print(f"   🔴 ПЛОХО: Много лишних символов")
    
    # 4. Конкретные примеры с именами (20 баллов)
    example_names = ['Анна', 'Марина', 'Елена', 'Ольга', 'Светлана', 'Ирина', 'Наталья', 'Татьяна', 'Виктория']
    found_names = [name for name in example_names if name in profile_text]
    print(f"\n4. КОНКРЕТНЫЕ ПРИМЕРЫ:")
    print(f"   Найденные имена: {found_names}")
    print(f"   Количество: {len(found_names)}")
    
    if len(found_names) >= 5:
        quality_score += 20
        print(f"   ✅ ОТЛИЧНО: {len(found_names)} примеров")
    elif len(found_names) >= 3:
        quality_score += 15
        print(f"   🟡 ХОРОШО: {len(found_names)} примеров")
    elif len(found_names) >= 1:
        quality_score += 10
        print(f"   🟠 УДОВЛЕТВОРИТЕЛЬНО: {len(found_names)} примеров")
    else:
        quality_score += 0
        print(f"   🔴 ПЛОХО: Нет конкретных примеров")
    
    # 5. Научная терминология (15 баллов)
    scientific_terms = [
        'нарциссизм', 'газлайтинг', 'манипуляция', 'проекция', 'триада',
        'макиавеллизм', 'психопатия', 'дизрегуляция', 'абьюз', 'травма'
    ]
    found_terms = [term for term in scientific_terms if term.lower() in profile_text.lower()]
    print(f"\n5. НАУЧНАЯ ТЕРМИНОЛОГИЯ:")
    print(f"   Найденные термины: {found_terms}")
    print(f"   Количество: {len(found_terms)}")
    
    if len(found_terms) >= 6:
        quality_score += 15
        print(f"   ✅ ОТЛИЧНО: {len(found_terms)} терминов")
    elif len(found_terms) >= 4:
        quality_score += 12
        print(f"   🟡 ХОРОШО: {len(found_terms)} терминов")
    elif len(found_terms) >= 2:
        quality_score += 8
        print(f"   🟠 УДОВЛЕТВОРИТЕЛЬНО: {len(found_terms)} терминов")
    else:
        quality_score += 0
        print(f"   🔴 ПЛОХО: Мало научных терминов")
    
    # 6. Цитаты и диалоги (15 баллов)
    quote_count = profile_text.count('"') + profile_text.count("'")
    print(f"\n6. ЦИТАТЫ И ДИАЛОГИ:")
    print(f"   Кавычек найдено: {quote_count}")
    
    if quote_count >= 20:
        quality_score += 15
        print(f"   ✅ ОТЛИЧНО: {quote_count} кавычек (много диалогов)")
    elif quote_count >= 10:
        quality_score += 12
        print(f"   🟡 ХОРОШО: {quote_count} кавычек")
    elif quote_count >= 5:
        quality_score += 8
        print(f"   🟠 УДОВЛЕТВОРИТЕЛЬНО: {quote_count} кавычек")
    else:
        quality_score += 0
        print(f"   🔴 ПЛОХО: Мало диалогов")
    
    # 7. Уникальность контента (10 баллов)
    sentences = profile_text.split('.')
    unique_sentences = len(set(sentence.strip() for sentence in sentences if sentence.strip()))
    print(f"\n7. УНИКАЛЬНОСТЬ КОНТЕНТА:")
    print(f"   Уникальных предложений: {unique_sentences}")
    
    if unique_sentences >= 80:
        quality_score += 10
        print(f"   ✅ ОТЛИЧНО: Высокая уникальность")
    elif unique_sentences >= 60:
        quality_score += 8
        print(f"   🟡 ХОРОШО: Средняя уникальность")
    else:
        quality_score += 5
        print(f"   🟠 УДОВЛЕТВОРИТЕЛЬНО: Низкая уникальность")
    
    print(f"\n📊 ИТОГОВАЯ ОЦЕНКА: {quality_score}/{max_score} ({quality_score/max_score*100:.1f}%)")
    
    if quality_score >= 100:
        print("🏆 ПРЕВОСХОДНО! Профессиональный детальный портрет")
    elif quality_score >= 80:
        print("🎉 ОТЛИЧНО! Высококачественный анализ")
    elif quality_score >= 60:
        print("🟡 ХОРОШО! Качественный анализ с недочетами")
    else:
        print("🔴 ТРЕБУЕТ УЛУЧШЕНИЙ! Много недостатков")
    
    return quality_score, max_score

async def test_professional_analysis():
    """Тестирует профессиональный анализ"""
    print("🎯 Генерирую профессиональный тест...")
    
    # Генерируем данные
    partner_profile = generate_partner_profile()
    answers = generate_realistic_answers()
    
    print(f"\n👤 ПРОФИЛЬ ПАРТНЕРА:")
    print(f"Имя: {partner_profile['name']}")
    print(f"Возраст: {partner_profile['age']} лет")
    print(f"Профессия: {partner_profile['profession']}")
    
    print(f"\n📝 ПРИМЕРЫ ТОКСИЧНЫХ ОТВЕТОВ:")
    print("=" * 60)
    for i, answer in enumerate(answers[:3], 1):
        print(f"{i}. {answer['question']}")
        print(f"   Ответ: {answer['answer']}")
        print()
    
    # Инициализируем AI
    ai_service = AIService()
    
    print(f"🤖 Запускаю профессиональный анализ...")
    start_time = time.time()
    
    try:
        result = await ai_service.profile_partner(
            answers=answers,
            user_id=999,
            partner_name=partner_profile['name'],
            partner_description=partner_profile['description'],
            use_cache=False
        )
        
        analysis_time = time.time() - start_time
        
        print(f"✅ Анализ завершен за {analysis_time:.2f} секунд")
        
        # Показываем результат
        profile_text = result.get('psychological_profile', '')
        
        print(f"\n📖 ПРОФЕССИОНАЛЬНЫЙ ПСИХОЛОГИЧЕСКИЙ ПОРТРЕТ:")
        print("=" * 80)
        print(profile_text)
        print("=" * 80)
        
        # Детальный анализ качества
        quality_score, max_score = analyze_quality(result, partner_profile['name'])
        
        return result, quality_score, max_score, analysis_time
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None, 0, 120, 0

async def main():
    """Главная функция"""
    print("🚀 ТЕСТИРОВАНИЕ ПРОФЕССИОНАЛЬНОГО АНАЛИЗА")
    print("=" * 80)
    
    result, score, max_score, time_taken = await test_professional_analysis()
    
    if result:
        print("\n" + "=" * 80)
        print("🎯 ИТОГИ ПРОФЕССИОНАЛЬНОГО ТЕСТИРОВАНИЯ")
        print("=" * 80)
        
        percentage = (score / max_score) * 100
        print(f"📊 Оценка качества: {score}/{max_score} ({percentage:.1f}%)")
        print(f"⏱️ Время анализа: {time_taken:.2f} секунд")
        print(f"💰 Стоимость: ~${result.get('cost_estimate', 0.15)}")
        
        if percentage >= 85:
            print("🏆 СИСТЕМА ИДЕАЛЬНА! Готова к продакшену!")
        elif percentage >= 70:
            print("🎉 ОТЛИЧНО! Система работает на высоком уровне!")
        elif percentage >= 55:
            print("🟡 ХОРОШО! Есть место для улучшений")
        else:
            print("🔴 ТРЕБУЕТ ДОРАБОТКИ! Много недостатков")

if __name__ == "__main__":
    asyncio.run(main()) 