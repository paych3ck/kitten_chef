import os

from user import User
from dbconnection import DbConnection
from miscs import convert_datetime_in_feed, \
    convert_datetime_in_chat, generate_random_password, \
    current_time, process_recipe, convert_comments_to_json, \
    process_notes
from forms import AddFriendForm, \
    UserSettingsForm, RegisterForm, LoginForm, \
    PasswordRecoveryForm, AddPostForm

from flask import Flask, request, render_template, \
    redirect, send_from_directory, url_for, flash, \
    jsonify, abort
from flask_mail import Mail, Message
from flask_login import LoginManager, login_user, \
    logout_user, login_required, current_user
from flask_socketio import SocketIO, emit, \
    join_room, leave_room
from werkzeug.security import generate_password_hash, \
    check_password_hash
from werkzeug.utils import secure_filename

# from yookassa import Configuration, Payment

application = Flask(__name__)
application.config.from_object('config')
application.jinja_env.globals.update(
    convert_datetime_in_feed=convert_datetime_in_feed,
    convert_datetime_in_chat=convert_datetime_in_chat
)
socketio = SocketIO(application)
login_manager = LoginManager(application)
mail = Mail(application)
db = DbConnection(application)

# Configuration.account_id = application.config['SHOP_ID']
# Configuration.secret_key = application.config['SHOP_SECRET_KEY']


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
    register_form = RegisterForm()

    if register_form.validate_on_submit():
        if register_form.password.data != register_form.confirm_password.data:
            flash('Пароли не совпадают!', category='error')
            return redirect(url_for('register'))

        username = register_form.username.data
        email = register_form.email.data
        password_hash = generate_password_hash(register_form.password.data)
        db.add_user((username, email, password_hash))

        html_body = render_template('welcome_mail.html', username=username)
        msg = Message('Добро пожаловать!', recipients=[email], html=html_body)
        mail.send(msg)

        return redirect(url_for('login'))

    return render_template('register.html', register_form=register_form)


@application.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        user_data = db.get_user_by_email(login_form.email.data)

        if user_data and check_password_hash(user_data['password_hash'],
                                             login_form.password.data):
            userlogin = User(user_data)
            login_user(userlogin)
            return redirect(url_for('feed'))

        flash('Ошибка авторизации!', category='error')

    return render_template('login.html', login_form=login_form)


@application.route('/password_recovery', methods=['GET', 'POST'])
def password_recovery():
    password_recovery_form = PasswordRecoveryForm()

    if password_recovery_form.validate_on_submit():
        email = password_recovery_form.email.data
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

    return render_template('password_recovery.html',
                           password_recovery_form=password_recovery_form)


@application.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@application.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(application.config['UPLOAD_FOLDER'], filename)


@socketio.on('leave')
def handle_leave(data):
    room = data['room']
    leave_room(room)


@socketio.on('join')
def handle_enter_chat(data):
    room = data['room']
    chat_user_id = data['chat_user_id']
    join_room(room)
    messages = db.get_messages_for_chat(current_user.id, chat_user_id)

    for message in messages:
        message['sent_at'] = convert_datetime_in_chat(message['sent_at'])

    emit('previous_messages', messages)


@socketio.on('message')
def handle_send_message(data):
    sender_id = current_user.id
    receiver_id = data['receiver_id']
    content = data['content']
    sent_at = current_time()
    db.add_message((sender_id, receiver_id, content, sent_at))
    data['sent_at'] = convert_datetime_in_chat(sent_at)
    emit('message', {**data}, room=data['room'])


@application.route('/messages')
@login_required
def messages():
    chats = db.get_chats_for_user_by_id(current_user.id)
    print(chats)
    return render_template('messages.html', chats=chats)


@application.route('/messages/<string:chat_username>', methods=['GET', 'POST'])
@login_required
def chat(chat_username):
    chat_user_info = db.get_user_by_username(chat_username)
    chat_user_id = chat_user_info['user_id']
    return render_template('chat.html', chat_username=chat_username,
                           chat_user_id=chat_user_id)


@application.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    user_settings_form = UserSettingsForm()

    if user_settings_form.validate_on_submit():
        user_id = current_user.id
        user_username = user_settings_form.username.data
        user_email = user_settings_form.email.data
        user_status = user_settings_form.status.data
        user_profile_picture = user_settings_form.profile_picture.data

        if current_user.username != user_username:
            if current_user.is_premium:
                db.update_user_username(user_id, user_username)

        if current_user.email != user_email:
            db.update_user_email(user_id, user_email)

        if current_user.status != user_status:
            db.update_user_status(user_id, user_status)

        if user_profile_picture:
            filename = secure_filename(user_profile_picture.filename)
            avatar_path = os.path.join('uploads/avatars/', str(user_id))
            os.makedirs(avatar_path, exist_ok=True)
            user_profile_picture.save(os.path.join(avatar_path, filename))
            db.update_user_profile_picture(user_id, f'{user_id}/{filename}')

        return redirect(url_for('settings'))

    return render_template('settings.html',
                           user_settings_form=user_settings_form)


@application.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    add_post_form = AddPostForm()

    if add_post_form.validate_on_submit():
        user_id = current_user.id
        content = add_post_form.content.data
        note_id = db.add_note(user_id, 'post')
        db.add_post_detail(note_id, content)
        return redirect(url_for('feed'))

    return render_template('add_post.html', add_post_form=add_post_form)


@application.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    if request.method == 'POST':
        recipe_name = request.form['recipe_name']
        ingredients, steps = process_recipe(request.form)
        user_id = current_user.id
        note_id = db.add_note(user_id, 'recipe')
        db.add_recipe_detail(note_id, recipe_name, ingredients, steps)
        return redirect(url_for('feed'))

    return render_template('add_recipe.html')


@application.route('/friends', methods=['GET', 'POST'])
@login_required
def friends():
    pending_invites = db.check_pending_invites(current_user.id)
    friends = db.get_all_friends(current_user.id)

    if request.method == 'POST':
        user_id = current_user.id
        action = request.form['action']
        friend_id = request.form.get(
            'invite_id') or request.form.get('friend_id')

        if action == 'accept':
            invite_id = request.form['invite_id']
            db.confirm_friend_request(user_id, invite_id)

        elif action in ['reject', 'delete']:
            db.delete_friend(user_id, friend_id)

        elif action == 'send_message':
            chat_username = db.get_user_by_id(friend_id)['username']
            return redirect(url_for('chat', chat_username=chat_username))

        return redirect(url_for('friends'))

    return render_template('friends.html',
                           pending_invites=pending_invites, friends=friends)


@application.route('/like', methods=['POST'])
def like_post():
    user_id = current_user.id
    note_id = request.json['note_id']

    if db.has_like(user_id, note_id):
        db.remove_like(user_id, note_id)
        return jsonify({'status': 'like removed'})

    else:
        db.add_like(user_id, note_id)
        return jsonify({'status': 'like added'})


@application.route('/favorite', methods=['POST'])
def favorite_post():
    user_id = current_user.id
    note_id = request.json['note_id']

    if db.has_favorite(user_id, note_id):
        db.remove_favorite(user_id, note_id)
        return jsonify({'status': 'favorite removed'})

    else:
        db.add_favorite(user_id, note_id)
        return jsonify({'status': 'favorite added'})


@application.route('/add-comment', methods=['POST'])
def comment():
    user_id = current_user.id
    note_id = request.json['note_id']
    content = request.json['content']
    db.add_comment(user_id, note_id, content)

    return jsonify({'status': 'success',
                    'username': current_user.username,
                    'profile_picture': current_user.profile_picture,
                    'content': content,
                    'timestamp': convert_datetime_in_feed(current_time())})


@application.route('/get-comments/<int:note_id>')
def get_comments(note_id):
    note_comments = db.get_comments_for_note(note_id)
    comments = convert_comments_to_json(note_comments)
    return jsonify(comments)


@application.route('/feed', methods=['GET', 'POST'])
@login_required
def feed():
    user_id = current_user.id
    notes = db.get_notes()
    notes = process_notes(db, notes, user_id)

    return render_template('feed.html', notes=notes)


@application.route('/likes')
@login_required
def likes():
    user_id = current_user.id
    liked_notes = db.get_notes(user_id=user_id, likes=True)
    notes = process_notes(db, liked_notes, user_id)

    return render_template('likes.html', notes=notes)


@application.route('/favorites')
@login_required
def favorites():
    user_id = current_user.id
    favorited_notes = db.get_notes(user_id=user_id, favorites=True)
    notes = process_notes(db, favorited_notes, user_id)
    return render_template('favorites.html', notes=notes)


@application.route('/user/<string:username>', methods=['GET', 'POST'])
@login_required
def user_profile(username):
    add_friend_form = AddFriendForm()
    user_info = db.get_user_by_username(username)

    if not user_info:
        abort(404)

    user_id = current_user.id
    friend_id = user_info['user_id']
    notes = db.get_notes(user_id=friend_id, notes=True)
    notes = process_notes(db, notes, friend_id)

    friendship_status = db.check_friendship_status(user_id, friend_id)

    if friendship_status == 'pending':
        add_friend_form.submit.label.text = 'Отменить заявку'

    if friendship_status == 'accepted':
        add_friend_form.submit.label.text = 'Удалить из друзей'

    if add_friend_form.validate_on_submit():
        if friendship_status == 'not_friends':
            db.send_friend_request(user_id, friend_id)

        if friendship_status in ['pending', 'accepted']:
            db.delete_friend(user_id, friend_id)

        return redirect(url_for('user_profile', username=username))

    return render_template('user_profile.html', user_info=user_info,
                           add_friend_form=add_friend_form,
                           friendship_status=friendship_status,
                           notes=notes)


@application.route('/premium')
@login_required
def premium():
    return render_template('premium.html')


if __name__ == '__main__':
    socketio.run(application, host='0.0.0.0', debug=True)
