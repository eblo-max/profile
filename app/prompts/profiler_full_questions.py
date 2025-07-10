"""
Полная версия профайлера партнера - 28 вопросов в 6 блоках
Основано на техническом задании с научным обоснованием
"""

from typing import Dict, List, Any, Tuple
from app.utils.enums import UrgencyLevel


# =================================
# БЛОК 1: НАРЦИССИЗМ И ГРАНДИОЗНОСТЬ (6 вопросов - убрал narcissism_q7)
# =================================

NARCISSISM_QUESTIONS = {
    "narcissism_q1": {
        "id": "narcissism_q1",
        "block": "narcissism",
        "weight": 3,  # Высокий вес
        "text": "Как ваш партнер реагирует на критику или замечания?",
        "context": "Оцените типичную реакцию партнера на конструктивную критику",
        "options": [
            "Выслушивает спокойно и благодарит за обратную связь",
            "Может расстроиться, но потом обдумывает сказанное",
            "Защищается и оправдывается, не принимая критику",
            "Раздражается и переходит в контратаку",
            "Агрессивно отвергает критику и обвиняет в ответ"
        ],
        "weights": [0, 1, 2, 3, 4]
    },
    
    "narcissism_q2": {
        "id": "narcissism_q2",
        "block": "narcissism",
        "weight": 3,
        "text": "Как ваш партнер относится к чужим успехам?",
        "context": "Реакция на достижения друзей, коллег или вас",
        "options": [
            "Искренне радуется и поздравляет",
            "Поздравляет, но с небольшой завистью",
            "Равнодушен к чужим успехам",
            "Обесценивает достижения или находит недостатки",
            "Злится и считает, что ему везет меньше"
        ],
        "weights": [0, 1, 2, 3, 4]
    },
    
    "narcissism_q3": {
        "id": "narcissism_q3",
        "block": "narcissism", 
        "weight": 3,
        "text": "Как ваш партнер описывает себя в разговорах?",
        "context": "Самовосприятие и самопрезентация",
        "options": [
            "Скромно, не выпячивая свои достоинства",
            "Уверенно, но без преувеличений",
            "Иногда преувеличивает свои достижения",
            "Часто подчеркивает свою исключительность",
            "Считает себя лучше большинства людей"
        ],
        "weights": [0, 1, 2, 3, 4]
    },
    
    "narcissism_q4": {
        "id": "narcissism_q4",
        "block": "narcissism",
        "weight": 3,
        "text": "Как ваш партнер реагирует на ваши переживания?",
        "context": "Эмпатия к эмоциональным состояниям",
        "options": [
            "Внимательно выслушивает и поддерживает",
            "Старается помочь, но не всегда понимает",
            "Иногда отвлекается, но в целом сочувствует",
            "Слушает невнимательно, быстро переводит тему на себя",
            "Обесценивает переживания или раздражается"
        ],
        "weights": [0, 1, 2, 3, 4]
    },
    
    "narcissism_q5": {
        "id": "narcissism_q5",
        "block": "narcissism",
        "weight": 2,
        "text": "Как ваш партнер строит отношения с другими людьми?",
        "context": "Способность к равноправным отношениям",
        "options": [
            "Легко находит общий язык, уважает границы",
            "В целом хорошо, но иногда может быть эгоистичным",
            "Относится к людям в зависимости от настроения",
            "Делит людей на полезных и бесполезных",
            "Использует людей для достижения своих целей"
        ],
        "weights": [0, 1, 2, 3, 4]
    },
    
    "narcissism_q6": {
        "id": "narcissism_q6",
        "block": "narcissism",
        "weight": 3,
        "text": "Как ваш партнер извиняется за свои ошибки?",
        "context": "Способность признавать вину и извиняться",
        "options": [
            "Искренне извиняется и старается исправить ситуацию",
            "Извиняется, но иногда с оговорками",
            "Извиняется неохотно, когда его принуждают",
            "Извиняется формально, не признавая вины",
            "Не извиняется, находит оправдания или обвиняет других"
        ],
        "weights": [0, 1, 2, 3, 4]
    }
}

# =================================
# БЛОК 2: КОНТРОЛЬ И МАНИПУЛЯЦИИ (6 вопросов - убрал control_q6 и control_q8)
# =================================

CONTROL_QUESTIONS = {
    "control_q1": {
        "id": "control_q1",
        "block": "control",
        "weight": 4,
        "text": "Как ваш партнер реагирует на ваши планы встретиться с друзьями?",
        "context": "Контроль социальных контактов",
        "options": [
            "Поддерживает и радуется за меня",
            "Нейтрально, иногда интересуется планами",
            "Иногда выражает недовольство, но не запрещает",
            "Часто недоволен, устраивает сцены",
            "Категорически против, запрещает встречи"
        ],
        "weights": [0, 1, 2, 3, 4]
    },
    
    "control_q2": {
        "id": "control_q2",
        "block": "control",
        "weight": 3,
        "text": "Как партнер относится к вашим личным вещам и пространству?",
        "context": "Уважение к личным границам",
        "options": [
            "Полностью уважает мои границы",
            "В основном уважает, иногда может нарушить",
            "Периодически роется в вещах без разрешения",
            "Часто проверяет телефон, сообщения",
            "Постоянно контролирует все мои вещи и действия"
        ],
        "weights": [0, 1, 2, 3, 4]
    },
    
    "control_q3": {
        "id": "control_q3",
        "block": "control",
        "weight": 4,
        "text": "Как ваш партнер реагирует на ваши успехи и достижения?",
        "context": "Отношение к независимости партнера",
        "options": [
            "Искренне радуется и поддерживает",
            "Радуется, но иногда может приревновать",
            "Реагирует нейтрально, без особого интереса",
            "Обесценивает или находит недостатки",
            "Злится, пытается помешать моим успехам"
        ],
        "weights": [0, 1, 2, 3, 4]
    },
    
    "control_q4": {
        "id": "control_q4",
        "block": "control",
        "weight": 3,
        "text": "Как происходят ваши совместные решения?",
        "context": "Демократичность в принятии решений",
        "options": [
            "Всегда обсуждаем и принимаем решения вместе",
            "Обычно советуемся, но иногда один решает сам",
            "Часто один из нас навязывает свое мнение",
            "Партнер принимает большинство решений единолично",
            "Партнер решает все, мое мнение не учитывается"
        ],
        "weights": [0, 1, 2, 3, 4]
    },
    
    "control_q5": {
        "id": "control_q5",
        "block": "control",
        "weight": 4,
        "text": "Как ваш партнер реагирует на ваши самостоятельные решения?",
        "context": "Толерантность к автономии",
        "options": [
            "Поддерживает мою самостоятельность",
            "В основном поддерживает, иногда может не согласиться",
            "Часто требует отчета о моих решениях",
            "Злится, если я что-то решаю без него",
            "Запрещает принимать решения самостоятельно"
        ],
        "weights": [0, 1, 2, 3, 4]
    },
    
    "control_q6": {
        "id": "control_q6",
        "block": "control",
        "weight": 3,
        "text": "Как ваш партнер относится к вашим увлечениям и хобби?",
        "context": "Поддержка личных интересов",
        "options": [
            "Активно поддерживает и интересуется",
            "Относится нейтрально, не мешает",
            "Иногда критикует, но в целом терпит",
            "Часто обесценивает, называет пустой тратой времени",
            "Запрещает заниматься тем, что мне нравится"
        ],
        "weights": [0, 1, 2, 3, 4]
    }
}

# =================================
# БЛОК 3: ГАЗЛАЙТИНГ И ИСКАЖЕНИЕ РЕАЛЬНОСТИ (5 вопросов - убрал gaslighting_q5)
# =================================

GASLIGHTING_QUESTIONS = {
    "gaslighting_q1": {
        "id": "gaslighting_q1",
        "block": "gaslighting",
        "weight": 4,
        "text": "Как ваш партнер реагирует, когда вы выражаете свои чувства?",
        "context": "Валидация эмоций",
        "options": [
            "Внимательно выслушивает и принимает",
            "Старается понять, иногда может не согласиться",
            "Иногда обесценивает, но в целом слушает",
            "Часто говорит, что я слишком чувствительна",
            "Полностью отрицает мои чувства и называет их неправильными"
        ],
        "weights": [0, 1, 2, 3, 4]
    },
    
    "gaslighting_q2": {
        "id": "gaslighting_q2",
        "block": "gaslighting",
        "weight": 4,
        "text": "Как ваш партнер ведет себя после конфликтов?",
        "context": "Отношение к разрешению конфликтов",
        "options": [
            "Обсуждает произошедшее и ищет решение",
            "Обычно мирится, но не всегда обсуждает проблему",
            "Делает вид, что ничего не произошло",
            "Обвиняет меня в том, что я все придумала",
            "Утверждает, что конфликта не было, я все выдумала"
        ],
        "weights": [0, 1, 2, 3, 4]
    },
    
    "gaslighting_q3": {
        "id": "gaslighting_q3",
        "block": "gaslighting",
        "weight": 3,
        "text": "Как ваш партнер относится к вашей памяти о событиях?",
        "context": "Подрыв доверия к собственной памяти",
        "options": [
            "Доверяет моей памяти и версии событий",
            "Иногда может не согласиться, но уважает мою точку зрения",
            "Периодически сомневается в моей памяти",
            "Часто утверждает, что я все неправильно помню",
            "Постоянно говорит, что у меня плохая память и я все путаю"
        ],
        "weights": [0, 1, 2, 3, 4]
    },
    
    "gaslighting_q4": {
        "id": "gaslighting_q4",
        "block": "gaslighting",
        "weight": 4,
        "text": "Как ваш партнер реагирует на ваши сомнения в отношениях?",
        "context": "Реакция на выражение сомнений",
        "options": [
            "Открыто обсуждает и старается разобраться",
            "Выслушивает, но может защищаться",
            "Иногда раздражается, но в целом слушает",
            "Обвиняет меня в паранойе и недоверии",
            "Говорит, что я сумасшедшая и все выдумываю"
        ],
        "weights": [0, 1, 2, 3, 4]
    },
    
    "gaslighting_q5": {
        "id": "gaslighting_q5",
        "block": "gaslighting",
        "weight": 3,
        "text": "Как ваш партнер объясняет свои противоречивые действия?",
        "context": "Способность признавать непоследовательность",
        "options": [
            "Честно объясняет и признает противоречия",
            "Обычно находит логичное объяснение",
            "Иногда уходит от ответа или меняет тему",
            "Отрицает противоречия и обвиняет меня в придирках",
            "Утверждает, что противоречий нет, я все неправильно понимаю"
        ],
        "weights": [0, 1, 2, 3, 4]
    }
}

# =================================
# БЛОК 4: ЭМОЦИОНАЛЬНАЯ РЕГУЛЯЦИЯ (4 вопроса - убрал emotion_q3) 
# =================================

EMOTION_QUESTIONS = {
    "emotion_q1": {
        "id": "emotion_q1",
        "block": "emotion",
        "weight": 4,
        "text": "Как ваш партнер выражает гнев?",
        "context": "Способы выражения негативных эмоций",
        "options": [
            "Спокойно обсуждает то, что его расстроило",
            "Иногда повышает голос, но быстро успокаивается",
            "Часто кричит, но не переходит на личности",
            "Оскорбляет, унижает, может бросать вещи",
            "Применяет физическую силу или угрожает"
        ],
        "weights": [0, 1, 2, 3, 4]
    },
    
    "emotion_q2": {
        "id": "emotion_q2",
        "block": "emotion",
        "weight": 3,
        "text": "Как часто у вашего партнера меняется настроение?",
        "context": "Эмоциональная стабильность",
        "options": [
            "Настроение стабильное, изменения предсказуемы",
            "Иногда бывают перепады, но в целом стабильно",
            "Настроение меняется довольно часто",
            "Резкие перепады настроения несколько раз в неделю",
            "Настроение меняется несколько раз в день непредсказуемо"
        ],
        "weights": [0, 1, 2, 3, 4]
    },
    
    "emotion_q3": {
        "id": "emotion_q3",
        "block": "emotion",
        "weight": 4,
        "text": "Как ваш партнер реагирует на ваши слезы или расстройство?",
        "context": "Эмпатия к эмоциональному состоянию",
        "options": [
            "Утешает и поддерживает",
            "Старается помочь, но иногда не знает как",
            "Иногда игнорирует, иногда утешает",
            "Раздражается и говорит перестать плакать",
            "Злится, оскорбляет или обвиняет в слабости"
        ],
        "weights": [0, 1, 2, 3, 4]
    },
    
    "emotion_q4": {
        "id": "emotion_q4",
        "block": "emotion",
        "weight": 3,
        "text": "Как ваш партнер ведет себя в стрессовых ситуациях?",
        "context": "Поведение под давлением",
        "options": [
            "Остается спокойным и рациональным",
            "Иногда нервничает, но в целом справляется",
            "Часто теряет самообладание, но не срывается на других",
            "Становится агрессивным, винит окружающих",
            "Полностью теряет контроль, может стать опасным"
        ],
        "weights": [0, 1, 2, 3, 4]
    }
}

# =================================
# БЛОК 5: ИНТИМНОСТЬ И ПРИНУЖДЕНИЕ (3 вопроса - убрал intimacy_q3)
# =================================

INTIMACY_QUESTIONS = {
    "intimacy_q1": {
        "id": "intimacy_q1",
        "block": "intimacy",
        "weight": 4,
        "text": "Как ваш партнер относится к вашим границам в интимности?",
        "context": "Уважение к согласию и границам",
        "options": [
            "Всегда спрашивает согласие и уважает границы",
            "Обычно уважает, иногда может настаивать",
            "Иногда игнорирует нежелание, но останавливается",
            "Часто принуждает и не принимает отказ",
            "Полностью игнорирует согласие и применяет принуждение"
        ],
        "weights": [0, 1, 2, 3, 4]
    },
    
    "intimacy_q2": {
        "id": "intimacy_q2",
        "block": "intimacy",
        "weight": 3,
        "text": "Как ваш партнер реагирует на ваши потребности в близости?",
        "context": "Внимание к потребностям партнера",
        "options": [
            "Внимательно выслушивает и учитывает мои потребности",
            "Старается понять, но не всегда получается",
            "Иногда учитывает, иногда фокусируется только на себе",
            "Редко интересуется моими потребностями",
            "Полностью игнорирует мои потребности и желания"
        ],
        "weights": [0, 1, 2, 3, 4]
    },
    
    "intimacy_q3": {
        "id": "intimacy_q3",
        "block": "intimacy",
        "weight": 4,
        "text": "Использует ли ваш партнер интимность для контроля?",
        "context": "Манипуляции через интимность",
        "options": [
            "Никогда не использует интимность для манипуляций",
            "Очень редко может намекать на связь между близостью и отношениями",
            "Иногда обижается при отказе в близости",
            "Часто угрожает разрывом при отказе в близости",
            "Постоянно шантажирует и принуждает через угрозы"
        ],
        "weights": [0, 1, 2, 3, 4]
    }
}

# =================================
# БЛОК 6: СОЦИАЛЬНОЕ ПОВЕДЕНИЕ (4 вопроса - без изменений)
# =================================

SOCIAL_QUESTIONS = {
    "social_q1": {
        "id": "social_q1",
        "block": "social",
        "weight": 3,
        "text": "Как ваш партнер ведет себя в компании других людей?",
        "context": "Социальное поведение и маски",
        "options": [
            "Ведет себя естественно, так же как наедине",
            "Иногда может быть более сдержанным или активным",
            "Заметно меняется в компании, но не кардинально",
            "Кардинально меняется, становится другим человеком",
            "Полностью другая личность, неузнаваемый"
        ],
        "weights": [0, 1, 2, 3, 4]
    },
    
    "social_q2": {
        "id": "social_q2",
        "block": "social",
        "weight": 4,
        "text": "Как ваш партнер относится к вашим друзьям и семье?",
        "context": "Изоляция от поддерживающего окружения",
        "options": [
            "Поддерживает ваши отношения с близкими",
            "В целом нормально, но не все друзья ему нравятся",
            "Иногда критикует близких, но не запрещает общение",
            "Часто критикует ваших друзей и ограничивает общение",
            "Запрещает видеться с друзьями и семьей"
        ],
        "weights": [0, 1, 2, 3, 4]
    },
    
    "social_q3": {
        "id": "social_q3",
        "block": "social",
        "weight": 3,
        "text": "Как окружающие относятся к вашему партнеру?",
        "context": "Восприятие партнера другими людьми",
        "options": [
            "Все друзья и семья его любят и уважают",
            "Большинство относится хорошо, есть нейтральные",
            "Отношение смешанное, есть как положительные, так и негативные мнения",
            "Многие высказывают сомнения или не одобряют",
            "Почти все предупреждают меня о нем"
        ],
        "weights": [0, 1, 2, 3, 4]
    },
    
    "social_q4": {
        "id": "social_q4",
        "block": "social",
        "weight": 4,
        "text": "Как ваш партнер реагирует на критику от других?",
        "context": "Реакция на внешнюю критику",
        "options": [
            "Выслушивает и анализирует критику",
            "Иногда защищается, но в целом принимает",
            "Часто обижается, но не мстит",
            "Злится и пытается отомстить критикам",
            "Впадает в ярость, может стать опасным"
        ],
        "weights": [0, 1, 2, 3, 4]
    }
}

# =================================
# ОСНОВНЫЕ ФУНКЦИИ
# =================================

def get_all_questions() -> Dict[str, Dict[str, Any]]:
    """Получить все вопросы профайлера"""
    all_questions = {}
    all_questions.update(NARCISSISM_QUESTIONS)
    all_questions.update(CONTROL_QUESTIONS)
    all_questions.update(GASLIGHTING_QUESTIONS)
    all_questions.update(EMOTION_QUESTIONS)
    all_questions.update(INTIMACY_QUESTIONS)
    all_questions.update(SOCIAL_QUESTIONS)
    return all_questions

def get_question_by_state(state_name: str) -> Dict[str, Any]:
    """Получить вопрос по имени состояния"""
    questions = get_all_questions()
    return questions.get(state_name)

def get_block_questions(block_name: str) -> Dict[str, Dict[str, Any]]:
    """Получить все вопросы блока"""
    all_questions = get_all_questions()
    return {k: v for k, v in all_questions.items() if v['block'] == block_name}

def calculate_total_questions() -> int:
    """Подсчитать общее количество вопросов"""
    return len(get_all_questions())

# =================================
# НАВИГАЦИЯ ПО ВОПРОСАМ (ОБНОВЛЕННАЯ ДЛЯ 28 ВОПРОСОВ)
# =================================

QUESTION_ORDER = [
    # Block 1: Narcissism (6 questions)
    "narcissism_q1", "narcissism_q2", "narcissism_q3", "narcissism_q4",
    "narcissism_q5", "narcissism_q6",
    
    # Block 2: Control (6 questions)  
    "control_q1", "control_q2", "control_q3", "control_q4",
    "control_q5", "control_q6",
    
    # Block 3: Gaslighting (5 questions)
    "gaslighting_q1", "gaslighting_q2", "gaslighting_q3", 
    "gaslighting_q4", "gaslighting_q5",
    
    # Block 4: Emotion (4 questions)
    "emotion_q1", "emotion_q2", "emotion_q3", "emotion_q4",
    
    # Block 5: Intimacy (3 questions)
    "intimacy_q1", "intimacy_q2", "intimacy_q3",
    
    # Block 6: Social (4 questions)
    "social_q1", "social_q2", "social_q3", "social_q4"
]

def get_next_question_state(current_state: str) -> str:
    """Получить следующее состояние вопроса"""
    try:
        current_index = QUESTION_ORDER.index(current_state)
        if current_index < len(QUESTION_ORDER) - 1:
            return QUESTION_ORDER[current_index + 1]
        else:
            return "reviewing_answers"
    except ValueError:
        return "reviewing_answers"

def get_previous_question_state(current_state: str) -> str:
    """Получить предыдущее состояние вопроса"""
    try:
        current_index = QUESTION_ORDER.index(current_state)
        if current_index > 0:
            return QUESTION_ORDER[current_index - 1]
        else:
            return "waiting_for_description"
    except ValueError:
        return "waiting_for_description"

def get_question_progress(current_state: str) -> Tuple[int, int]:
    """Получить прогресс прохождения (текущий вопрос, общее количество)"""
    try:
        current_index = QUESTION_ORDER.index(current_state)
        return (current_index + 1, len(QUESTION_ORDER))
    except ValueError:
        return (1, len(QUESTION_ORDER))

def get_block_by_question(question_state: str) -> str:
    """Получить блок по состоянию вопроса"""
    question = get_question_by_state(question_state)
    return question.get('block', 'unknown') if question else 'unknown'

def format_question_text(question_data: Dict[str, Any], question_num: int, total_questions: int) -> str:
    """Форматировать текст вопроса для отображения"""
    if not question_data:
        return "Ошибка: вопрос не найден"
    
    # Блок эмодзи
    block_emoji = {
        "narcissism": "🧠",
        "control": "🎯", 
        "gaslighting": "🔄",
        "emotion": "💭",
        "intimacy": "💕",
        "social": "👥"
    }
    
    block_names = {
        "narcissism": "Нарциссизм и грандиозность",
        "control": "Контроль и манипуляции",
        "gaslighting": "Газлайтинг и искажение реальности", 
        "emotion": "Эмоциональная регуляция",
        "intimacy": "Интимность и принуждение",
        "social": "Социальное поведение"
    }
    
    block = question_data.get('block', 'unknown')
    emoji = block_emoji.get(block, '❓')
    block_name = block_names.get(block, 'Неизвестный блок')
    
    # Прогресс-бар
    progress_percentage = (question_num / total_questions) * 100
    progress_bar_length = 10
    filled_length = int(progress_bar_length * question_num // total_questions)
    progress_bar = "█" * filled_length + "░" * (progress_bar_length - filled_length)
    
    question_text = f"""📋 **Вопрос {question_num} из {total_questions}**

{emoji} **Блок:** {block_name}

📊 **Прогресс:** {progress_bar} {progress_percentage:.0f}%

❓ **{question_data['text']}**

💭 _{question_data['context']}_

Выберите наиболее подходящий вариант:"""
    
    return question_text

# =================================
# СИСТЕМА ПОДСЧЕТА БАЛЛОВ
# =================================

def calculate_weighted_scores(answers: Dict[str, int]) -> Dict[str, Any]:
    """Подсчитать взвешенные баллы с учетом весов вопросов"""
    all_questions = get_all_questions()
    
    # Подсчет по блокам
    block_scores = {
        "narcissism": 0,
        "control": 0, 
        "gaslighting": 0,
        "emotion": 0,
        "intimacy": 0,
        "social": 0
    }
    
    block_max_scores = {
        "narcissism": 0,
        "control": 0,
        "gaslighting": 0, 
        "emotion": 0,
        "intimacy": 0,
        "social": 0
    }
    
    # Подсчет баллов для каждого ответа
    for question_id, answer_index in answers.items():
        question = all_questions.get(question_id)
        if not question:
            continue
            
        block = question['block']
        weight = question['weight']
        answer_weight = question['weights'][answer_index] if answer_index < len(question['weights']) else 0
        
        # Баллы = вес вопроса * вес ответа
        score = weight * answer_weight
        block_scores[block] += score
        
        # Максимальный возможный балл для этого вопроса
        max_score = weight * max(question['weights'])
        block_max_scores[block] += max_score
    
    # Нормализация баллов до 0-10 по каждому блоку
    normalized_block_scores = {}
    for block in block_scores:
        if block_max_scores[block] > 0:
            normalized_score = (block_scores[block] / block_max_scores[block]) * 10
            normalized_block_scores[block] = round(normalized_score, 1)
        else:
            normalized_block_scores[block] = 0.0
    
    # Общий взвешенный балл риска
    total_score = sum(block_scores.values())
    total_max_score = sum(block_max_scores.values())
    overall_risk_score = (total_score / total_max_score * 100) if total_max_score > 0 else 0
    
    return {
        "block_scores": normalized_block_scores,
        "overall_risk_score": round(overall_risk_score, 1),
        "urgency_level": get_urgency_level(overall_risk_score),
        "raw_scores": block_scores,
        "max_scores": block_max_scores
    }

def get_urgency_level(risk_score: float) -> UrgencyLevel:
    """Определить уровень срочности по баллу риска"""
    if risk_score >= 75:
        return UrgencyLevel.CRITICAL
    elif risk_score >= 50:
        return UrgencyLevel.HIGH
    elif risk_score >= 25:
        return UrgencyLevel.MEDIUM
    else:
        return UrgencyLevel.LOW

def get_safety_alerts(answers: Dict[str, int]) -> List[str]:
    """Генерировать предупреждения безопасности на основе критических ответов"""
    alerts = []
    all_questions = get_all_questions()
    
    # Критические паттерны для немедленного реагирования
    critical_patterns = {
        "control_q1": [3],  # Контроль времени - последний ответ
        "control_q2": [3],  # Изоляция от друзей/семьи
        "control_q4": [3],  # Полный финансовый контроль
        "control_q5": [3],  # Агрессивное нарушение границ
        "control_q7": [3],  # Угрозы и запугивание
        "gaslighting_q1": [3],  # Постоянное отрицание реальности
        "gaslighting_q2": [3],  # Обесценивание чувств
        "gaslighting_q3": [3],  # Никогда не берет вину на себя
        "emotion_q1": [3],  # Вспышки ярости с угрозами
        "intimacy_q1": [3],  # Принуждение в интимности
        "social_q1": [3]   # Кардинально разное поведение дома/на публике
    }
    
    alert_messages = {
        "control_q1": "⚠️ КОНТРОЛЬ ВРЕМЕНИ: Партнер контролирует каждый ваш шаг",
        "control_q2": "⚠️ ИЗОЛЯЦИЯ: Партнер изолирует вас от поддерживающего окружения",
        "control_q4": "⚠️ ФИНАНСОВОЕ ПРИНУЖДЕНИЕ: Полный контроль над вашими деньгами",
        "control_q5": "⚠️ НАРУШЕНИЕ ГРАНИЦ: Агрессивная реакция на ваши границы",
        "control_q7": "🚨 УГРОЗЫ: Партнер использует запугивание и угрозы",
        "gaslighting_q1": "🚨 ГАЗЛАЙТИНГ: Систематическое искажение реальности",
        "gaslighting_q2": "⚠️ ЭМОЦИОНАЛЬНОЕ НАСИЛИЕ: Обесценивание ваших чувств",
        "gaslighting_q3": "⚠️ ОТСУТСТВИЕ ОТВЕТСТВЕННОСТИ: Никогда не признает вину",
        "emotion_q1": "🚨 ФИЗИЧЕСКАЯ УГРОЗА: Неконтролируемые вспышки ярости",
        "intimacy_q1": "🚨 ПРИНУЖДЕНИЕ: Игнорирование согласия в интимности",
        "social_q1": "⚠️ ДВОЙНАЯ ЛИЧНОСТЬ: Кардинально разное поведение"
    }
    
    for question_id, critical_answers in critical_patterns.items():
        answer_index = answers.get(question_id)
        if answer_index in critical_answers:
            alert = alert_messages.get(question_id)
            if alert:
                alerts.append(alert)
    
    return alerts

def validate_full_answers(answers: Dict[str, int]) -> Tuple[bool, str]:
    """Валидировать полный набор ответов"""
    expected_questions = set(QUESTION_ORDER)
    provided_questions = set(answers.keys())
    
    if len(provided_questions) != len(expected_questions):
        missing = expected_questions - provided_questions
        if missing:
            return False, f"Отсутствуют ответы на вопросы: {', '.join(missing)}"
        
    # Проверка валидности ответов
    all_questions = get_all_questions()
    for question_id, answer_index in answers.items():
        question = all_questions.get(question_id)
        if not question:
            return False, f"Неизвестный вопрос: {question_id}"
            
        if not isinstance(answer_index, int) or answer_index < 0 or answer_index >= len(question['options']):
            return False, f"Некорректный ответ для вопроса {question_id}: {answer_index}"
    
    return True, "Все ответы валидны" 