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
