import re
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

@dataclass
class ParsedReminder:
    title: str
    datetime_obj: Optional[datetime]
    raw_text: str
    confidence: float
    is_parsed: bool

class ReminderParser:

    WEEKDAYS_AR = {
        "الاحد": 6, "الاثنين": 0, "الثلاثاء": 1,
        "الاربعاء": 2, "الخميس": 3, "الجمعة": 4, "السبت": 5,
    }
    WEEKDAYS_EN = {
        "sunday": 6, "monday": 0, "tuesday": 1, "wednesday": 2,
        "thursday": 3, "friday": 4, "saturday": 5,
    }

    def parse(self, text: str) -> ParsedReminder:
        raw = text.strip()
        dt = self._extract_datetime(raw)
        title = self._extract_title(raw)
        return ParsedReminder(
            title=title, datetime_obj=dt, raw_text=raw,
            confidence=0.85 if dt else 0.0, is_parsed=dt is not None,
        )

    def _extract_datetime(self, text: str) -> Optional[datetime]:
        now = datetime.now()
        result = now.replace(second=0, microsecond=0)
        hour, minute, am_pm = None, 0, None

        # Extract time
        m = re.search(r"(\d+)(?::(\d+))?\s*(AM|PM|am|pm)?", text)
        if m:
            hour = int(m.group(1))
            if m.group(2): minute = int(m.group(2))
            if m.group(3): am_pm = m.group(3).upper()

        # AM/PM from context
        if re.search(r"PM|pm|مساء", text): am_pm = "PM"
        elif re.search(r"AM|am|صباح", text): am_pm = "AM"

        if hour is None:
            return None

        if am_pm == "PM" and hour < 12: hour += 12
        elif am_pm == "AM" and hour == 12: hour = 0
        result = result.replace(hour=hour, minute=minute)

        # Relative day
        if re.search(r"tomorrow|tomorrow", text, re.IGNORECASE):
            return result + timedelta(days=1)
        if re.search(r"today|tonight", text, re.IGNORECASE):
            return result

        # English weekday
        for day, num in self.WEEKDAYS_EN.items():
            if re.search(day, text, re.IGNORECASE):
                ahead = (num - now.weekday()) % 7 or 7
                return result + timedelta(days=ahead)

        # Arabic weekday (normalized - no diacritics)
        normalized = text.replace("\u0623", "\u0627").replace("\u0625", "\u0627").replace("\u0622", "\u0627")
        for day, num in self.WEEKDAYS_AR.items():
            if day in normalized:
                ahead = (num - now.weekday()) % 7 or 7
                return result + timedelta(days=ahead)

        if result < now:
            result += timedelta(days=1)
        return result

    def _extract_title(self, text: str) -> str:
        t = re.sub(r"(remind me (to|about|of)?)", "", text, flags=re.IGNORECASE)
        t = re.sub(r"\d+(?::\d+)?\s*(AM|PM|am|pm)?", "", t)
        t = re.sub(r"\b(tomorrow|today|tonight|next|at)\b", "", t, flags=re.IGNORECASE)
        for day in self.WEEKDAYS_EN:
            t = re.sub(day, "", t, flags=re.IGNORECASE)
        return re.sub(r"\s+", " ", t).strip(" .,") or text