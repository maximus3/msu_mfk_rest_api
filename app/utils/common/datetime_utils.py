from datetime import datetime

import dateutil.tz


def get_datetime_msk_tz(dt: datetime | str | None = None) -> datetime:
    dt = dt or datetime.utcnow()
    if isinstance(dt, str):
        if dt.lower()[-1] == 'z':
            dt = dt[:-1]
        dt = datetime.fromisoformat(dt)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=dateutil.tz.tzutc())
    else:
        dt = dt.astimezone(dateutil.tz.tzutc())
    return dt.astimezone(dateutil.tz.gettz('Europe/Moscow')).replace(
        tzinfo=None
    )
