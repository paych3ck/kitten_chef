from dbconnection import DbConnection
from chefuser import User

from flask import Flask, request, render_template, \
    redirect, url_for, flash, abort
from flask_mail import Mail, Message
from flask_login import LoginManager, login_user, \
    logout_user, login_required, current_user
from flask_socketio import SocketIO, send, emit, \
    join_room, leave_room, send
from werkzeug.security import generate_password_hash, check_password_hash


application = Flask(__name__)
application.config.from_object('config')
socketio = SocketIO(application)
login_manager = LoginManager(application)
mail = Mail(application)
db = DbConnection(application)


@login_manager.user_loader
def load_user(user_id):
    user_data = db.get_user_by_id(user_id)
    return User(user_data)


@application.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


@application.route('/')
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
        html_body = render_template('mail.html')
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

        flash('Ошибка авторизации')

    return render_template('login.html')


@application.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@application.route('/messages')
@login_required
def messages():
    messages_ = db.get_messages_for_user_by_id(current_user.id)
    return render_template('messages.html', chats=messages_)


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


@application.route('/settings')
@login_required
def settings():
    return render_template('settings.html')


@application.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    if request.method == 'POST':
        user_id = current_user.id
        content = request.form['post_text']
        db.add_post((user_id, content))
        return redirect(url_for('feed'))

    return render_template('add_post.html')


@application.route('/post/<int:post_id>')
def post(post_id):
    post_info = db.get_post_by_id(post_id)
    return render_template('post.html', post_info=post_info)


@application.route('/feed')
@login_required
def feed():
    posts = db.get_all_posts()
    return render_template('feed.html', posts=posts)


@application.route('/user/<string:username>')
def user_profile(username):
    user_info = db.get_user_by_username(username)

    if not user_info:
        abort(404)

    return render_template('user_profile.html', user_info=user_info)


@application.route('/buy_premium')
@login_required
def buy_premium():
    return render_template('buy_premium.html')


if __name__ == '__main__':
    socketio.run(application, debug=True)
