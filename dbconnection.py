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

    def get_messages_for_chat(self, user_id_1, user_id_2):
        self.connect()
        cursor = self.connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        query = '''SELECT m.message_id, m.sender_id, s.username AS sender_username,
            m.receiver_id, r.username AS receiver_username, m.content, m.sent_at
            FROM messages m
            JOIN users s ON m.sender_id = s.user_id
            JOIN users r ON m.receiver_id = r.user_id
            WHERE (m.sender_id = %s AND m.receiver_id = %s)
            OR (m.sender_id = %s AND m.receiver_id = %s)
            ORDER BY m.sent_at
        '''

        cursor.execute(query, (user_id_1, user_id_2, user_id_2, user_id_1))
        res = cursor.fetchall()
        cursor.close()
        self.disconnect()
        return res

    def get_messages_for_user_by_id(self, user_id):
        self.connect()
        cursor = self.connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)

        query = '''WITH LastMessages AS (
                   SELECT
                   m1.sender_id,
                   m1.receiver_id,
                   m1.content AS last_message_text,
                   m1.sent_at AS last_message_sent_at,
                   ROW_NUMBER() OVER (
                   PARTITION BY
                   CASE WHEN m1.sender_id = %s THEN m1.receiver_id ELSE m1.sender_id END
                   ORDER BY
                   m1.sent_at DESC
                   ) AS rn
                   FROM
                   messages m1
                   WHERE
                   m1.sender_id = %s OR m1.receiver_id = %s
                   )
                   SELECT
                   u.username AS chat_partner_username,
                   lm.last_message_text,
                   lm.last_message_sent_at
                   FROM
                   LastMessages lm
                   JOIN
                   users u ON u.user_id = CASE WHEN lm.sender_id = %s THEN lm.receiver_id ELSE lm.sender_id END
                   WHERE
                   lm.rn = 1'''

        cursor.execute(query, (user_id, user_id, user_id, user_id))
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
