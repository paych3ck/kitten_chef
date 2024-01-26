import psycopg2
import psycopg2.sql
from flask import Flask, request, render_template
from flask_login import LoginManager, UserMixin, login_user, \
    logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash


class DbConnection:
    def __init__(self, host, database_name, user, password):
        self.host = host
        self.database_name = database_name
        self.user = user
        self.password = password

    def connect(self):
        self.connection = psycopg2.connect(host=self.host,
                                           database=self.database_name,
                                           user=self.user,
                                           password=self.password)

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def add_user(self, data):
        self.connect()
        cursor = self.connection.cursor()
        query = '''INSERT INTO users(username, email, password_hash)
                   VALUES(%s, %s, %s)'''
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()
        self.disconnect()

    def get_user_by(self, ident, val):
        self.connect()
        cursor = self.connection.cursor()

        query = psycopg2.sql.SQL('''SELECT *
                   FROM users
                   WHERE {pkey} = %s''').format(pkey=psycopg2.sql.Identifier(ident))

        cursor.execute(query, (val, ))
        self.connection.commit()
        res = cursor.fetchone()
        cursor.close()
        self.disconnect()
        return res


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
login_manager = LoginManager(app)
db = DbConnection('localhost', 'KittenChef', 'postgres', 'postgres')


class User(UserMixin):
    # TODO: Как буд-то get_from_db() и create() очень сильно похожи на костыли. Переделать в дальнейшем.
    def get_from_db(self, user_id, db):
        self.__user = db.get_user_by(
            'user_id', user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user[0])

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True


@login_manager.user_loader
def load_user(user_id):
    return User().get_from_db(user_id, db)


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
        user = db.get_user_by('email', request.form['email'])

        if user and check_password_hash(user[3],
                                        request.form['password']):
            userlogin = User().create(user)
            login_user(userlogin)
            return 'УДАЧНО'

        return 'НЕУДАЧНО'

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'Вы не авторизованы'


if __name__ == '__main__':
    app.run(debug=True)
