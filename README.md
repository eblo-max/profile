# 🤖 PsychoDetective Bot

> AI-powered Telegram bot for relationship analysis using criminal psychology methods

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![aiogram](https://img.shields.io/badge/aiogram-3.x-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-blue.svg)
![Redis](https://img.shields.io/badge/Redis-7+-red.svg)

## 🎯 Overview

PsychoDetective is the first AI-powered Telegram bot that uses criminal psychology methods to analyze relationships and protect users from toxic behavior. Built with cutting-edge AI models and scientific research.

### ✨ Key Features

- 🚩 **Text Analysis** - Detect toxicity in messages using criminal psychology
- 👤 **Partner Profiling** - Create psychological profiles of partners
- 💕 **Compatibility Testing** - Advanced compatibility analysis
- 🛡️ **Manipulation Detection** - Identify gaslighting and emotional manipulation
- 📊 **Daily Content** - Psychology tips and relationship advice
- 💎 **Premium Features** - Advanced analysis with Claude AI

## 🏗️ Tech Stack

- **Language**: Python 3.12+
- **Bot Framework**: aiogram 3.x
- **Web Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 16+ with asyncpg
- **Cache**: Redis 7+ with hiredis
- **AI Primary**: Claude-3-Sonnet API
- **AI Fallback**: OpenAI GPT-4 API
- **Deployment**: Railway
- **Monitoring**: Sentry + Loguru
- **Testing**: Pytest + pytest-asyncio

## 🚀 Quick Deploy to Railway

### 1. Fork & Clone

```bash
git clone https://github.com/your-username/psycho-detective-bot.git
cd psycho-detective-bot
```

### 2. Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/your-username/psycho-detective-bot)

### 3. Add Required Services

In Railway dashboard:
1. **Add PostgreSQL Database**
2. **Add Redis**

### 4. Environment Variables

Set these in Railway environment variables:

```env
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_here
CLAUDE_API_KEY=your_claude_api_key
SECRET_KEY=your-super-secret-key-here

# Optional but recommended
OPENAI_API_KEY=your_openai_api_key
SENTRY_DSN=your_sentry_dsn

# Auto-configured by Railway
DATABASE_URL=${DATABASE_URL}
REDIS_URL=${REDIS_URL}
PORT=${PORT}
```

### 5. Deploy & Migrate

Railway will automatically:
- Install dependencies
- Run database migrations
- Start the bot

## 🛠️ Local Development

### Prerequisites

- Python 3.12+
- PostgreSQL (or SQLite for dev)
- Redis
- Telegram Bot Token
- Claude API Key

### Setup

1. **Clone repository**
```bash
git clone https://github.com/your-username/psycho-detective-bot.git
cd psycho-detective-bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Environment setup**
```bash
cp .env.example .env
# Edit .env with your values
```

4. **Database setup**
```bash
alembic upgrade head
```

5. **Run locally**
```bash
python -m app.main
```

## 📊 Project Structure

```
app/
├── main.py                    # FastAPI + aiogram entry point
├── bot/
│   ├── handlers/             # All aiogram handlers
│   ├── keyboards/            # All keyboards
│   ├── middlewares/          # Middleware
│   └── states.py            # FSM states
├── core/
│   ├── config.py            # Configuration
│   ├── database.py          # Async SQLAlchemy
│   ├── redis.py            # Redis client
│   └── logging.py          # Loguru settings
├── models/                  # SQLAlchemy models
├── services/               # Business logic
├── api/                    # FastAPI endpoints
├── utils/                 # Utilities
└── prompts/              # AI prompts
```

## 🔧 Configuration

### Core Settings

- `DEBUG`: Development mode (default: False)
- `SECRET_KEY`: Application secret key
- `TELEGRAM_BOT_TOKEN`: Telegram bot token
- `CLAUDE_API_KEY`: Claude AI API key
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string

### AI Configuration

- `CLAUDE_MODEL`: Claude model (default: claude-3-sonnet-20240229)
- `OPENAI_MODEL`: OpenAI model (default: gpt-4-turbo-preview)
- `MAX_CONCURRENT_AI_REQUESTS`: Concurrent requests limit
- `AI_REQUEST_TIMEOUT`: Request timeout in seconds

### Rate Limiting

- `RATE_LIMIT_REQUESTS`: Requests per window
- `RATE_LIMIT_WINDOW`: Time window in seconds
- `FREE_ANALYSES_LIMIT`: Free tier analysis limit

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_ai_service.py
```

## 📝 API Documentation

Once deployed, visit:
- `/docs` - Swagger UI (development only)
- `/redoc` - ReDoc documentation (development only)
- `/health` - Health check endpoint

## 🔒 Security Features

- ✅ Rate limiting per user
- ✅ Input validation and sanitization
- ✅ SQL injection protection
- ✅ Async session management
- ✅ Error handling and logging
- ✅ GDPR compliant data handling

## 📈 Monitoring

### Health Checks

- Database connectivity
- Redis connectivity
- AI service availability
- Bot connectivity

### Logging

- Structured logging with Loguru
- Request/response tracking
- Error tracking with Sentry
- Performance metrics

## 🚨 Error Handling

The bot implements comprehensive error handling:

- Graceful AI service failures with fallbacks
- Database transaction rollbacks
- User-friendly error messages
- Automatic retry mechanisms
- Circuit breaker patterns

## 🔄 Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 🎮 Bot Commands

- `/start` - Initialize bot and onboarding
- `/menu` - Show main menu
- `/analyze` - Quick text analysis
- `/profile` - User profile management
- `/help` - Help and support
- `/support` - Contact support

## 💎 Premium Features

- Unlimited analyses
- Advanced AI models
- Priority support
- Detailed reporting
- Export capabilities

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is proprietary software. All rights reserved.

## 📞 Support

- 📧 Email: support@psychodetective.bot
- 💬 Telegram: [@psychodetective_support](https://t.me/psychodetective_support)
- 📖 Documentation: [docs.psychodetective.bot](https://docs.psychodetective.bot)

## 🙏 Acknowledgments

- Criminal psychology research from Harvard Psychology Lab
- AI models from Anthropic and OpenAI
- Open source community for tools and libraries

---

**⚠️ Disclaimer**: This bot is for educational and informational purposes only. For serious relationship issues, please consult with professional therapists or counselors. 