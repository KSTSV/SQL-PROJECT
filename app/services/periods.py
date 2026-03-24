import re
from datetime import datetime


class PeriodFormatError(ValueError):
    pass


def parse_period(period_str: str) -> tuple[datetime, datetime]:
    value = period_str.strip()

    if re.fullmatch(r"\d{4}", value):
        year = int(value)
        return datetime(year, 1, 1, 0, 0, 0), datetime(year, 12, 31, 23, 59, 59)

    if re.fullmatch(r"\d{4}-\d{4}", value):
        start_year, end_year = map(int, value.split("-"))
        if start_year > end_year:
            raise PeriodFormatError("Начальный год не может быть больше конечного")
        return datetime(start_year, 1, 1, 0, 0, 0), datetime(end_year, 12, 31, 23, 59, 59)

    if ":" in value:
        left, right = value.split(":", maxsplit=1)
        start = datetime.strptime(left.strip(), "%Y-%m-%d")
        end = datetime.strptime(right.strip(), "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        if start > end:
            raise PeriodFormatError("Дата начала не может быть больше даты конца")
        return start, end

    raise PeriodFormatError("Неверный формат периода. Используйте 2025, 2024-2025 или 2025-01-01:2025-12-31")
