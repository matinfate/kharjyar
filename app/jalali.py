import datetime

import jdatetime


def to_jalali_str(value: datetime.date) -> str:
    return jdatetime.date.fromgregorian(date=value).strftime("%Y/%m/%d")


def parse_jalali(value: str) -> datetime.date:
    try:
        year, month, day = (int(p) for p in value.replace("-", "/").split("/"))
        return jdatetime.date(year, month, day).togregorian()
    except ValueError as exc:
        raise ValueError("jalali_date must look like 1405/08/01") from exc


def month_range(year: int, month: int) -> tuple[datetime.date, datetime.date]:
    first_day = jdatetime.date(year, month, 1)
    if month == 12:
        next_first_day = jdatetime.date(year + 1, 1, 1)
    else:
        next_first_day = jdatetime.date(year, month + 1, 1)

    last_day = next_first_day - datetime.timedelta(days=1)
    return first_day.togregorian(), last_day.togregorian()
