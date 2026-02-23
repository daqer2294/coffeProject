from datetime import datetime
from config import BUSINESS_TZ


def get_today():
    return datetime.now(BUSINESS_TZ).date()
