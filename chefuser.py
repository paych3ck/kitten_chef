from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, user_data):
        self.__user = user_data

    @property
    def id(self):
        return str(self.__user[0])

    @property
    def username(self):
        return str(self.__user[1])

    @property
    def email(self):
        return str(self.__user[2])

    @property
    def status(self):
        return str(self.__user[4])

    @property
    def profile_picture(self):
        return str(self.__user[5])

    @property
    def registration_date(self):
        return str(self.__user[6])

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True
