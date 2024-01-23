import psycopg2
from flask import Flask

app = Flask(__name__)


def connect_db():
    conn = psycopg2.connect(host='localhost',
                            database='KittenChef',
                            user='postgres',
                            password='postgres')
    return conn


@app.route('/register')
def register():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        '''INSERT INTO users(username, email, password_hash)
           VALUES('test', 'tst', 'test')''')
    conn.commit()
    cur.close()
    conn.close()
    return 'Страница регистрации'


@app.route('/login')
def login():
    return 'Страница авторизации'


if __name__ == '__main__':
    app.run(debug=True)
