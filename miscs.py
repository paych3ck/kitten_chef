import secrets
import string
import datetime


def generate_random_password(length=15):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


def current_time():
    return datetime.datetime.now()


def convert_datetime_in_feed(time):
    months = [
        "января", "февраля", "марта", "апреля", "мая", "июня",
        "июля", "августа", "сентября", "октября", "ноября", "декабря"
    ]
    month_idx = time.month - 1
    return time.strftime("%d {} %Y %H:%M").format(months[month_idx])


def convert_datetime_in_chat(time):
    return time.strftime("%d.%m.%Y %H:%M:%S")
