# MeeSaya Telegram Bot

MeeSaya (မီးဆရာ) is a wise, practical, and friendly Myanmar Energy Consultant Telegram bot. It provides advice on solar power systems, battery recommendations, and energy calculations in Burmese language.

## Features

- Telegram webhook integration
- AI-powered responses using Google Gemini via OpenRouter
- Solar system calculator for Myanmar market
- Chat history storage in PostgreSQL
- Burmese language interface

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in your API keys
4. Initialize the database: `python init_db.py`
5. Run the app: `python main.py`

## Deployment

This app is designed to run on platforms like Railway or Heroku. Use the Procfile for deployment.

## Environment Variables

- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `TELEGRAM_BOT_TOKEN`: Telegram bot token
- `DATABASE_URL`: PostgreSQL database URL
- `ADMIN_TELEGRAM_ID`: Admin Telegram user ID
- `PORT`: Port to run the app (default 8000)
- `APP_PUBLIC_URL`: Public URL for webhook setup# meesaya_telegram
