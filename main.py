from dbconnection import DbConnection
from chefuser import User

from flask import Flask, request, render_template
from flask_login import LoginManager, login_user, \
    logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
login_manager = LoginManager(app)
db = DbConnection('localhost', 'KittenChef', 'postgres', 'postgres')


@login_manager.user_loader
def load_user(user_id):
    user_data = db.get_user_by_id(user_id)
    return User(user_data)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['name']
        email = request.form['email']
        password_hash = generate_password_hash(request.form['password'])
        db.add_user((username, email, password_hash))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_data = db.get_user_by_email(request.form['email'])

        if user_data and check_password_hash(user_data['password_hash'],
                                             request.form['password']):
            userlogin = User(user_data)
            login_user(userlogin)
            return 'УДАЧНО'

        return 'НЕУДАЧНО'

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'Вы не авторизованы'


@app.route('/messages')
@login_required
def list_messages():
    messages = db.get_messages_for_user_by_id(current_user.id)
    return render_template('list_messages.html', messages=messages)


@app.route('/messages/<string:receiver_name>', methods=['GET', 'POST'])
@login_required
def send_message(receiver_name):
    if request.method == 'POST':
        content = request.form['message']
        receiver_id = db.get_user_by_username(receiver_name)['user_id']
        db.add_message((current_user.id, receiver_id, content))

    return render_template('send_message.html')


@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')


@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    if request.method == 'POST':
        user_id = current_user.id
        content = request.form['post_text']
        db.add_post((user_id, content))

    return render_template('add_post.html')


@app.route('/post/<int:post_id>')
def post(post_id):
    post_info = db.get_post_by_id(post_id)
    return render_template('post.html', post_info=post_info)


@app.route('/feed')
@login_required
def feed():
    posts = db.get_all_posts()
    return render_template('feed.html', posts=posts)


@app.route('/user/<string:username>')
def user_profile(username):
    user_info = db.get_user_by_username(username)

    if user_info:
        return render_template('user_profile.html', user_info=user_info)

    return


@app.route('/buy_premium')
@login_required
def buy_premium():
    return render_template('buy_premium.html')


if __name__ == '__main__':
    app.run(debug=True)
