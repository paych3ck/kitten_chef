import psycopg2
import psycopg2.extras
import psycopg2.sql


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

    def add_post(self, data):
        self.connect()
        cursor = self.connection.cursor()
        query = '''INSERT INTO posts(user_id, content)
                   VALUES(%s, %s)'''
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()
        self.disconnect()

    def add_message(self, data):
        self.connect()
        cursor = self.connection.cursor()
        query = '''INSERT INTO messages(sender_id, receiver_id, content)
                   VALUES(%s, %s, %s)'''
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()
        self.disconnect()

    def add_user(self, data):
        self.connect()
        cursor = self.connection.cursor()
        query = '''INSERT INTO users(username, email, password_hash)
                   VALUES(%s, %s, %s)'''
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()
        self.disconnect()

    def get_all_posts(self):
        self.connect()
        cursor = self.connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        query = '''SELECT posts.*, users.username
                   FROM posts
                   INNER JOIN users ON posts.user_id = users.user_id'''
        cursor.execute(query)
        res = cursor.fetchall()
        cursor.close()
        self.disconnect()
        return res

    def get_messages_for_user_by_id(self, user_id):
        self.connect()
        cursor = self.connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)

        query = '''SELECT
                messages.sender_id,
                messages.receiver_id,
                messages.content,
                messages.sent_at,
                users.username AS receiver_name
                FROM messages
                JOIN users ON messages.receiver_id = users.user_id
                WHERE messages.sender_id = %s OR messages.receiver_id = %s'''

        cursor.execute(query, (user_id, user_id))
        res = cursor.fetchall()
        cursor.close()
        self.disconnect()
        return res

    def __get_post_by(self, column_name, value):
        self.connect()
        cursor = self.connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)

        query = psycopg2.sql.SQL('''SELECT *
                   FROM posts
                   WHERE {pkey} = %s''').format(
            pkey=psycopg2.sql.Identifier(column_name)
        )
        cursor.execute(query, (value, ))
        res = cursor.fetchone()
        cursor.close()
        self.disconnect()
        return res

    def get_post_by_id(self, value):
        return self.__get_post_by('post_id', value)

    def __get_user_by(self, column_name, value):
        self.connect()
        cursor = self.connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)

        query = psycopg2.sql.SQL('''SELECT *
                   FROM users
                   WHERE {pkey} = %s''').format(
            pkey=psycopg2.sql.Identifier(column_name)
        )

        cursor.execute(query, (value, ))
        self.connection.commit()
        res = cursor.fetchone()
        cursor.close()
        self.disconnect()
        return res

    def get_user_by_username(self, value):
        return self.__get_user_by('username', value)

    def get_user_by_email(self, value):
        return self.__get_user_by('email', value)

    def get_user_by_id(self, value):
        return self.__get_user_by('user_id', value)
