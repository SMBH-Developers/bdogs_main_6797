from datetime import datetime, timedelta


__all__ = ["get_date_by_weekday"]


def get_date_by_weekday(day: str):
    days = {'понедельник': 0, 'вторник': 1, 'среда': 2,
            'четверг': 3, 'пятница': 4, 'суббота': 5, 'воскресенье': 6}

    today = datetime.now()

    target_weekday = days[day.lower()]
    days_ahead = (target_weekday - today.weekday())

    day_date = today + timedelta(days=days_ahead)
    return day_date
