from dbconnection import DbConnection
from chefuser import User

from flask import Flask, request, render_template, \
    redirect, url_for, flash, abort
from flask_mail import Mail, Message
from flask_login import LoginManager, login_user, \
    logout_user, login_required, current_user
from flask_socketio import SocketIO, send, emit, \
    join_room, leave_room, send
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash

#from yookassa import Configuration, Payment

# import uuid
import secrets
import string

class NewPostForm(FlaskForm):
    postForm = TextAreaField('О чем расскажем?', validators=[DataRequired()])
    submit = SubmitField('Опубликовать')

application = Flask(__name__)
application.config.from_object('config')
socketio = SocketIO(application)
login_manager = LoginManager(application)
mail = Mail(application)
db = DbConnection(application)

# Configuration.account_id = application.config['SHOP_ID']
# Configuration.secret_key = application.config['SHOP_SECRET_KEY']


def generate_random_password(length=15):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


@login_manager.user_loader
def load_user(user_id):
    user_data = db.get_user_by_id(user_id)
    return User(user_data)


@application.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html')


@application.errorhandler(401)
def unauthorized(error):
    return redirect(url_for('login'))


@application.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('feed'))

    return redirect(url_for('login'))


@application.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['name']
        email = request.form['email']
        password_hash = generate_password_hash(request.form['password'])
        db.add_user((username, email, password_hash))

        html_body = render_template('welcome_mail.html', username=username)
        msg = Message('Добро пожаловать!', recipients=[email], html=html_body)
        mail.send(msg)

        return redirect(url_for('login'))

    return render_template('register.html')


@application.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_data = db.get_user_by_email(request.form['email'])

        if user_data and check_password_hash(user_data['password_hash'],
                                             request.form['password']):
            userlogin = User(user_data)
            login_user(userlogin)
            return redirect(url_for('feed'))

        flash('Ошибка авторизации!', category='error')

    return render_template('login.html')


@application.route('/password_recovery', methods=['GET', 'POST'])
def password_recovery():
    if request.method == 'POST':
        email = request.form['email']
        user_data = db.get_user_by_email(email)

        if user_data:
            new_password = generate_random_password()

            username = user_data['username']

            html_body = render_template(
                'password_recovery_mail.html', new_password=new_password,
                username=username)

            msg = Message('Восстановление пароля', recipients=[
                          email], html=html_body)
            mail.send(msg)

            db.update_user_password(
                email, generate_password_hash(new_password))

            return redirect(url_for('login'))

        flash('Пользователь с такой почтой не найден!', category='error')

    return render_template('password_recovery.html')


@application.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@application.route('/messages')
@login_required
def messages():
    # messages_ = db.get_messages_for_user_by_id(current_user.id)
    return render_template('messages.html')  # , chats=messages_)


# @application.route('/messages/<string:chat_username>', methods=['GET', 'POST'])
# @login_required
# def send_message(chat_username):
#     chat_user_info = db.get_user_by_username(chat_username)
#     chat_user_id = chat_user_info['user_id']
#     messages = db.get_messages_for_chat(current_user.id, chat_user_id)

#     if request.method == 'POST':
#         content = request.form['message']
#         receiver_id = db.get_user_by_username(chat_username)['user_id']
#         db.add_message((current_user.id, receiver_id, content))

#     return render_template('send_message.html', messages=messages)


@application.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        user_id = current_user.id
        user_username = request.form['username']
        user_email = request.form['email']
        user_status = request.form['status']
        user_profile_picture = request.form['profile_picture']

        if current_user.username != user_username:
            db.update_user_username(user_id, user_username)

        if current_user.email != user_email:
            db.update_user_email(user_id, user_email)

        if current_user.status != user_status:
            db.update_user_status(user_id, user_status)

        if current_user.profile_picture != user_profile_picture:
            db.update_user_profile_picture(user_id, user_status)

        return redirect(url_for('settings'))

    return render_template('settings.html')

# @application.route('/post/<int:post_id>')
# def post(post_id):
#     post_info = db.get_post_by_id(post_id)
#     return render_template('post.html', post_info=post_info)

@application.route('/friends')
@login_required
def friends():
    return render_template('friends.html')


@application.route('/feed', methods=['GET', 'POST'])
@login_required
def feed():
    posts = db.get_all_posts()
    new_post_form = NewPostForm()

    print(posts)
    if new_post_form.validate_on_submit():
        user_id = current_user.id
        content = new_post_form.postForm.data
        db.add_post((user_id, content))
        return redirect(url_for('feed'))
    
    return render_template('feed.html', posts=posts, new_post_form=new_post_form)


@application.route('/user/<string:username>')
def user_profile(username):
    user_info = db.get_user_by_username(username)

    if not user_info:
        abort(404)

    return render_template('user_profile.html', user_info=user_info)


@application.route('/premium')
@login_required
def premium():
    return render_template('premium.html')


if __name__ == '__main__':
    socketio.run(application, host='0.0.0.0', debug=True)
