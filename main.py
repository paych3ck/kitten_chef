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

        if user_data and check_password_hash(user_data[3],
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


@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    if request.method == 'POST':
        user_id = current_user.id
        content = request.form['post_text']
        db.add_post((user_id, content))

    return render_template('add_post.html')


@app.route('/feed')
def feed():
    return render_template('feed.html')


if __name__ == '__main__':
    app.run(debug=True)
