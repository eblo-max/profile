# Psychology AI Bot 🧠

AI-powered система психологического анализа через Telegram бота с использованием множественных специализированных AI сервисов.

## 🚀 Возможности (2025)

- 🔥 **Современный AI стек** - топ-5 лучших AI сервисов 2025 года
- 🧠 **Multi-modal анализ** - текст + изображения через Gemini 2.0
- 📊 **Научно обоснованные результаты** с кросс-валидацией
- 🎯 **Constitutional AI** - этичность и безопасность анализа
- ⚡ **Async архитектура** для высокой производительности
- 🔄 **Real-time обработка** с FastAPI + Webhook/Polling
- 🌐 **2M+ context window** для глубокого анализа больших текстов

## Архитектура

### 🚀 AI Сервисы (СОВРЕМЕННАЯ АРХИТЕКТУРА 2025)
- **Claude 3.5 Sonnet** - главный анализ и синтез ✅
- **OpenAI GPT-4o** - заменяет IBM Watson ✅
- **Google Gemini 2.0 Flash** - заменяет Google Cloud NL + Azure ⚡
- **Cohere Command-R+** - заменяет Lexalytics + Receptiviti ⚡
- **HuggingFace Transformers** - заменяет AWS Rekognition ⚡

### 📉 Deprecated сервисы (заменены):
- ~~IBM Watson~~ → **OpenAI GPT-4o**
- ~~Azure Cognitive~~ → **Google Gemini 2.0**
- ~~Google Cloud NL~~ → **Google Gemini 2.0**
- ~~AWS Rekognition~~ → **HuggingFace Transformers**
- ~~Crystal API~~ → **OpenAI GPT-4o**
- ~~Receptiviti~~ → **Cohere Command-R+**
- ~~Lexalytics~~ → **Cohere Command-R+**

### Технологии
- **Python 3.12+** с async/await
- **PostgreSQL 16+** с AsyncPG
- **Redis 7.2+** для кэширования
- **FastAPI** для webhook API
- **python-telegram-bot 21.0+**
- **SQLAlchemy 2.0+** async ORM

## Установка

### 1. Клонирование
```bash
git clone https://github.com/eblo-max/profile.git
cd profile
```

### 2. Виртуальное окружение
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения
```bash
cp .env.example .env
# Отредактируйте .env файл с вашими API ключами
```

### 5. Настройка базы данных
```bash
# Установите PostgreSQL и Redis
# Создайте базу данных psychology_bot
createdb psychology_bot
```

## Конфигурация

### 🔑 API Ключи (2025)
Получите API ключи для современных сервисов:

#### **✅ ОСНОВНЫЕ (обязательные):**
1. **Telegram Bot** - [@BotFather](https://t.me/botfather)
2. **Anthropic Claude** - [console.anthropic.com](https://console.anthropic.com/)

#### **⚡ СОВРЕМЕННЫЕ AI (рекомендуемые):**
3. **OpenAI GPT-4o** - [platform.openai.com](https://platform.openai.com/)
4. **Google Gemini** - [makersuite.google.com](https://makersuite.google.com/)
5. **Cohere Command-R+** - [dashboard.cohere.ai](https://dashboard.cohere.ai/)
6. **HuggingFace** - [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

#### **📉 DEPRECATED (необязательные):**
7. ~~Microsoft Azure~~ - [portal.azure.com](https://portal.azure.com/)
8. ~~Google Cloud~~ - [console.cloud.google.com](https://console.cloud.google.com/)
9. ~~AWS~~ - [aws.amazon.com](https://aws.amazon.com/)
10. ~~Crystal API~~ - [crystalknows.com](https://www.crystalknows.com/)
11. ~~Receptiviti~~ - [receptiviti.com](https://www.receptiviti.com/)

### Переменные окружения (.env)
```env
# Основные
TELEGRAM_BOT_TOKEN=your_bot_token
ANTHROPIC_API_KEY=your_anthropic_key
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/psychology_bot
REDIS_URL=redis://localhost:6379

# IBM Watson
IBM_WATSON_API_KEY=your_watson_key
IBM_WATSON_URL=your_watson_url

# ... остальные API ключи
```

## Запуск

### Режим разработки (Polling)
```bash
python -m src.main
```

### Продакшен с Webhook
```bash
# Установите WEBHOOK_URL в .env
WEBHOOK_URL=https://your-domain.com

# Запуск с uvicorn
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Docker (опционально)
```bash
docker-compose up -d
```

## Использование

1. **Запустите бота** - `/start`
2. **Начните анализ** - `/analyze`
3. **Загрузите данные** - текст, изображения
4. **Получите результат** - детальный психологический портрет

## Структура проекта

```
src/
├── main.py                 # Точка входа
├── bot/                    # Telegram бот
│   ├── handlers/          # Обработчики команд
│   ├── keyboards/         # Клавиатуры
│   ├── states/           # FSM состояния
│   └── middlewares/      # Middleware
├── ai/                    # AI клиенты
│   ├── anthropic_client.py
│   ├── watson_client.py
│   ├── analysis_engine.py
│   └── prompts/
├── validators/            # Валидация результатов
├── database/             # Модели и подключения
├── utils/                # Утилиты
└── config/               # Конфигурация
```

## API Эндпоинты

- `GET /` - статус API
- `GET /health` - проверка здоровья
- `POST /webhook` - Telegram webhook

## Разработка

### Тестирование
```bash
pytest tests/
```

### Линтинг и форматирование
```bash
black src/
ruff check src/
```

### Миграции базы данных
```bash
# Будут добавлены Alembic миграции
```

## Roadmap

- [ ] Интеграция всех AI сервисов
- [ ] Система кросс-валидации
- [ ] Web интерфейс для просмотра результатов
- [ ] Экспорт отчетов в PDF
- [ ] Многоязычная поддержка
- [ ] Telegram Mini App
- [ ] API для внешних интеграций

## Лицензия

MIT License

## Поддержка

Создайте issue в GitHub или свяжитесь с разработчиком.

---

**⚠️ Важно:** Этот проект предназначен для образовательных и исследовательских целей. Результаты анализа не являются медицинским диагнозом. 