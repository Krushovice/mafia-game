#!/usr/bin/env bash
set -euo pipefail

# Simple local runner for the Telegram bot (long-polling)
# Usage: set BOT_TELEGRAM_TOKEN and optionally BOT_API_URL, then run this script.

export PYTHONPATH=src

if [ -z "${BOT_TELEGRAM_TOKEN-}" ]; then
  echo "Environment variable BOT_TELEGRAM_TOKEN is not set. Create .env or export it." >&2
  echo "See .env.example" >&2
  exit 1
fi

: "${BOT_API_URL:=http://localhost:8000}"

echo "Starting bot with API_URL=${BOT_API_URL}"
python -m src.bot.main
