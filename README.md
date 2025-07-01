# Psychology AI Bot 🧠

AI-powered система психологического анализа через Telegram бота с использованием множественных специализированных AI сервисов.

## Возможности

- 🔍 **Многоуровневый анализ** через 8+ AI сервисов
- 📊 **Научно обоснованные результаты** с кросс-валидацией
- 🎯 **Полная прозрачность** источников данных
- ⚡ **Async архитектура** для высокой производительности
- 🔄 **Real-time обработка** с FastAPI + Webhook/Polling

## Архитектура

### AI Сервисы
- **IBM Watson** - Personality Insights
- **Azure Cognitive** - эмоциональный анализ
- **Google Cloud NL** - анализ сущностей
- **AWS Rekognition** - анализ лиц
- **Crystal API** - DISC профилирование
- **Receptiviti** - психолингвистика
- **Lexalytics** - продвинутый sentiment
- **Claude (Anthropic)** - синтез результатов

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

### API Ключи
Получите API ключи для всех сервисов:

1. **Telegram Bot** - [@BotFather](https://t.me/botfather)
2. **Anthropic Claude** - [console.anthropic.com](https://console.anthropic.com/)
3. **IBM Watson** - [cloud.ibm.com](https://cloud.ibm.com/)
4. **Microsoft Azure** - [portal.azure.com](https://portal.azure.com/)
5. **Google Cloud** - [console.cloud.google.com](https://console.cloud.google.com/)
6. **AWS** - [aws.amazon.com](https://aws.amazon.com/)
7. **Crystal API** - [crystalknows.com](https://www.crystalknows.com/)
8. **Receptiviti** - [receptiviti.com](https://www.receptiviti.com/)

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