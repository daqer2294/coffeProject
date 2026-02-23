import os
from dataclasses import dataclass
from zoneinfo import ZoneInfo


BUSINESS_TZ = ZoneInfo("Asia/Irkutsk")


@dataclass
class Settings:
    BOT_TOKEN: str
    DATABASE_URL: str
    ADMIN_IDS: list[int]


def _parse_admin_ids(raw: str | None) -> list[int]:
    if not raw:
        return []
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


def get_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN")
    database_url = os.getenv("DATABASE_URL")
    admin_ids = _parse_admin_ids(os.getenv("ADMIN_IDS"))

    if not bot_token:
        raise RuntimeError("BOT_TOKEN is not set")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    return Settings(
        BOT_TOKEN=bot_token,
        DATABASE_URL=database_url,
        ADMIN_IDS=admin_ids,
    )


settings = get_settings()