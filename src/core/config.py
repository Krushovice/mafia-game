from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class DataBaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 20
    max_overflow: int = 10


class BotConfig(BaseModel):
    token: str
    api_url: str = "http://localhost:8000"


class TMAConfig(BaseModel):
    enabled: bool = False
    bot_token: str = ""  # for initData validation (same as bot token)
    url: str = "http://localhost:3000"  # TMA frontend URL


class UvicornConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    workers: int = 1


class FastAPIConfig(BaseModel):
    title: str = "Mafia Game API"
    debug: bool = False
    root_path: str = ""
    cors_origins: list[str] = [
        "https://web.telegram.org",
        "https://*.web.telegram.org",
    ]


class LoggingConfig(BaseModel):
    level: str = "INFO"
    fmt: str = "%(asctime)s %(levelname)s %(name)s: %(message)s"


class Settings(BaseSettings):
    """Application settings read from environment (prefix APP_CONFIG__).

    Nested keys use `__` delimiter, e.g. `APP_CONFIG__BOT__TOKEN`.
    """

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=(".env",),
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
        env_file_encoding="utf-8",
        validate_default=False,
        extra="ignore",  # ignore bot-specific vars like BOT_TELEGRAM_TOKEN, TMA_URL
    )

    db: DataBaseConfig
    bot: BotConfig | None = None
    tma: TMAConfig = TMAConfig()
    uvicorn: UvicornConfig = UvicornConfig()
    api: FastAPIConfig = FastAPIConfig()
    logging: LoggingConfig = LoggingConfig()


settings = Settings()
