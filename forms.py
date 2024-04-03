from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import EmailField, \
    StringField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length


class RegisterForm(FlaskForm):
    username = StringField('ЛОГИН', validators=[
                           DataRequired(), Length(max=10)])
    email = EmailField('E-MAIL', validators=[DataRequired(), Email()])
    password = PasswordField('ПРИДУМАЙТЕ ПАРОЛЬ', validators=[
                             DataRequired(), Length(max=15)])
    confirm_password = PasswordField(
        'ПОВТОРИТЕ ПАРОЛЬ', validators=[DataRequired(), Length(max=15)])
    submit = SubmitField('ЗАРЕГИСТРИРОВАТЬСЯ')


class LoginForm(FlaskForm):
    email = EmailField('E-MAIL', validators=[DataRequired(), Email()])
    password = PasswordField('ПАРОЛЬ', validators=[
                             DataRequired(), Length(max=15)])
    submit = SubmitField('ВХОД В АККАУНТ')


class PasswordRecoveryForm(FlaskForm):
    email = EmailField('E-MAIL', validators=[DataRequired(), Email()])
    submit = SubmitField('ВОССТАНОВИТЬ')


class AddFriendForm(FlaskForm):
    submit = SubmitField('Добавить в друзья')


class NewPostForm(FlaskForm):
    postForm = TextAreaField('О чем расскажем?', validators=[DataRequired()])
    submit = SubmitField('Опубликовать')


class UserSettingsForm(FlaskForm):
    username = StringField('Имя пользователя:')
    email = EmailField('Адрес электронной почты:',
                       validators=[Email()])
    status = StringField('Статус:')
    profile_picture = FileField('Аватар (изображение):')
    submit = SubmitField('Сохранить изменения')
