try:
    # pydantic v2 moved BaseSettings to pydantic-settings
    from pydantic_settings import BaseSettings  # type: ignore
except Exception:
    from pydantic import BaseSettings  # type: ignore


class BotSettings(BaseSettings):
    telegram_token: str
    api_url: str = "http://localhost:8000"
    # Optional comma-separated list: BOT_ADMIN_TELEGRAM_IDS="123,456"
    admin_telegram_ids: str = ""

    class Config:
        env_prefix = "BOT_"


settings = BotSettings()
