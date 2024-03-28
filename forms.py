from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import EmailField, \
    StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email


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
