# Telegram Bot Setup

## Development (Polling Mode)

For local development, run the bot separately in polling mode:

```bash
cd /home/krusha/projects/mafia-game
PYTHONPATH=src BOT_TELEGRAM_TOKEN='YOUR_TOKEN' BOT_TMA_URL='https://your-tunnel-url/webapp' BOT_API_URL='http://localhost:8080' python -m src.bot.main
```

The API runs in Docker and serves the frontend + webhook endpoints, but the bot runs locally to have internet access.

## Production (Webhook Mode)

For production, simply set `BOT_WEBHOOK_URL` in `.env`:

```
BOT_WEBHOOK_URL=https://your-domain.ru/webhook
```

When the API starts, it will automatically:
1. Set the webhook with Telegram
2. Handle all incoming updates via `/webhook` endpoint
3. Process commands through aiogram dispatcher

No separate bot process needed in production!

## Migration: Polling → Webhook

1. Stop local bot process (Ctrl+C)
2. Set `BOT_WEBHOOK_URL=https://your-domain.ru/webhook` in `.env`
3. Restart API container: `docker-compose up -d --build api`
4. Verify webhook: `curl http://your-domain.ru/webhook/info`
