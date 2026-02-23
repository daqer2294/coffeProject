import os
from dataclasses import dataclass
from zoneinfo import ZoneInfo

BUSINESS_TZ = ZoneInfo("Asia/Irkutsk")


@dataclass
class Settings:
    BOT_TOKEN: str
    DATABASE_URL: str
    ADMIN_IDS: list[int]


def get_settings() -> Settings:
    return Settings(
        BOT_TOKEN=os.getenv("BOT_TOKEN", "8090286212:AAGZH7pP9au6rbOCGYUXHKGyFrGrHLy-s1A"),
        DATABASE_URL=os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://daqer@localhost:5432/coffee_db"
        ),
        ADMIN_IDS=[398548230, 312805873]  # сюда вставишь свой telegram id
    )


settings = get_settings()
