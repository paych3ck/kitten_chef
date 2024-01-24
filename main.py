import psycopg2
from flask import Flask, request, render_template


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

    def add_user(self, data):
        cursor = self.connection.cursor()
        query = '''INSERT INTO users(username, email, password_hash)
                   VALUES(%s, %s, %s)'''
        cursor.execute(query, data)
        self.connection.commit()
        # cursor.close()
        return cursor.fetchone()

    def check_user(self, email):
        cursor = self.connection.cursor()
        query = '''SELECT COUNT(1)
                   FROM users
                   WHERE email = %s'''
        cursor.execute(query, email)
        self.connection.commit()
        cursor.close()

    def disconnect(self):
        if self.connection:
            self.connection.close()


app = Flask(__name__)
db = DbConnection('localhost', 'KittenChef', 'postgres', 'postgres')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        db.connect()
        username = request.form['name']
        email = request.form['email']
        password = request.form['password']
        db.add_user((username, email, password))
        db.disconnect()

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db.connect()
        email = request.form['email']
        print(db.check_user((email, )))

    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
