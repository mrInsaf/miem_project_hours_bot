from datetime import datetime, timedelta
from user import User


def str_to_date(str_date: str):
    return datetime.strptime(str_date, '%d.%m.%Y')


def count_weekdays(date_of_finish: str):
    end_date = datetime.strptime(date_of_finish, "%d.%m.%Y").date()
    start_date = datetime.now().date()
    # Разница между датами
    delta = end_date - start_date

    # Полное количество дней между датами
    total_days = delta.days

    # Вычисляем количество полных недель в интервале
    full_weeks = total_days // 7

    # Остаток от деления на 7 дает количество дней в последней неполной неделе
    remaining_days = total_days % 7

    # Вычисляем количество воскресений в последней неполной неделе
    remaining_sundays = max(0, min(remaining_days - 1, 1))

    # Вычисляем общее количество воскресений в интервале
    total_sundays = full_weeks + remaining_sundays

    # Количество рабочих дней - общее количество дней минус количество воскресений
    weekdays = total_days - total_sundays

    return weekdays


def correct_date(needed_hours:int, hours_per_day:int):
    days_until_complete = timedelta(needed_hours / hours_per_day)
    corrected_date = datetime.now().date() + days_until_complete
    return corrected_date.strftime("%d.%m.%Y")


def calculate_total_lag(user: User, factual_hours: int):
    current_date = str_to_date(datetime.now().strftime('%d.%m.%Y'))
    registration_date = str_to_date(user.registration_date)
    days_worked = (current_date - registration_date).days
    hours_per_day = user.hours_per_day
    theoretical_hours = days_worked * hours_per_day
    return theoretical_hours - factual_hours

