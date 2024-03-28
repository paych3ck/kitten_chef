from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, user_data):
        self.__user = user_data

    @property
    def id(self):
        return str(self.__user['user_id'])

    @property
    def username(self):
        return str(self.__user['username'])

    @property
    def email(self):
        return str(self.__user['email'])

    @property
    def status(self):
        return str(self.__user['status'])

    @property
    def profile_picture(self):
        return str(self.__user['profile_picture'])

    @property
    def registration_date(self):
        return str(self.__user['registration_date'])

    @property
    def is_premium(self):
        return int(self.__user['is_premium'])

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True
