from datetime import datetime as dt, timedelta
from enum import Enum
import re


class Config(Enum):
    WEEKEND_DAYS = {5, 6}
    DATE_FORMAT = "%d.%m.%Y"


class Utils:
    @staticmethod
    def shift_to_monday(currdate: dt) -> dt:
        return currdate + timedelta(days=(7 - currdate.weekday()))

    @staticmethod
    def validate_email(email: str) -> bool:
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def generate_note_title(content: str) -> str:
        words = re.sub(r"[^\w\s]", "", content).split()
        return "_".join(words[:3]).lower()
