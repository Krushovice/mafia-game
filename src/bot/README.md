Telegram bot scaffold for the mafia-game project

Setup

1. Create a small virtualenv and install the bot requirements:

```bash
python -m pip install -r requirements-bot.txt
```

2. Set environment variables:

```bash
export BOT_TELEGRAM_TOKEN="<your-token>"
export BOT_API_URL="http://localhost:8000"
```

3. Run the bot:

```bash
python -m src.bot.main
```

Notes
- This is a minimal scaffold: handlers call the HTTP API endpoints under `BOT_API_URL`.
- Extend handlers in `src/bot/handlers.py` to add mission flows and authentication logic.
