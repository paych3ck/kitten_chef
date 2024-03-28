import secrets
import string


def generate_random_password(length=15):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


def convert_datetime(time):
    months = [
        "января", "февраля", "марта", "апреля", "мая", "июня",
        "июля", "августа", "сентября", "октября", "ноября", "декабря"
    ]
    month_idx = time.month - 1
    return time.strftime("%d {} %Y %H:%M").format(months[month_idx])
