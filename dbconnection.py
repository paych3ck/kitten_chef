import mysql.connector


class DbConnection:
    def __init__(self, app):
        self.host = app.config['DB_HOST']
        self.database_name = app.config['DB_NAME']
        self.user = app.config['DB_USER']
        self.password = app.config['DB_PASS']

    def connect(self):
        self.connection = mysql.connector.connect(host=self.host,
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
        cursor = self.connection.cursor(dictionary=True)
        query = '''SELECT posts.*, users.username, users.profile_picture
                    FROM posts
                    INNER JOIN users ON posts.user_id = users.user_id
                    ORDER BY posts.created_at DESC;
                    '''
        cursor.execute(query)
        res = cursor.fetchall()
        cursor.close()
        self.disconnect()
        return res

    def get_messages_for_chat(self, user_id_1, user_id_2):
        self.connect()
        cursor = self.connection.cursor(dictionary=True)
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
        cursor = self.connection.cursor(dictionary=True)

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
        cursor = self.connection.cursor(buffered=True, dictionary=True)

        query = f'''SELECT *
                   FROM posts
                   WHERE {column_name} = %s'''

        cursor.execute(query, (value, ))
        res = cursor.fetchone()
        cursor.close()
        self.disconnect()
        return res

    def get_post_by_id(self, value):
        return self.__get_post_by('post_id', value)

    def __get_user_by(self, column_name, value):
        self.connect()
        cursor = self.connection.cursor(buffered=True, dictionary=True)

        query = f'''SELECT *
                   FROM users
                   WHERE {column_name} = %s'''

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

    def update_user_password(self, email, password):
        self.connect()
        cursor = self.connection.cursor(buffered=True, dictionary=True)

        query = '''UPDATE users
                   SET password_hash = %s
                   WHERE email = %s'''

        values = (password, email)
        cursor.execute(query, values)
        self.connection.commit()
        cursor.close()
        self.disconnect()

    def __update_user_info_by(self, id, column_name, value):
        self.connect()
        cursor = self.connection.cursor(buffered=True, dictionary=True)

        query = f'''UPDATE users
                   SET {column_name} = %s
                   WHERE user_id = %s'''

        values = (value, id)
        cursor.execute(query, values)
        self.connection.commit()
        cursor.close()
        self.disconnect()

    def update_user_username(self, id, value):
        return self.__update_user_info_by(id, 'username', value)

    def update_user_email(self, id, value):
        return self.__update_user_info_by(id, 'email', value)

    def update_user_status(self, id, value):
        return self.__update_user_info_by(id, 'status', value)

    def update_user_profile_picture(self, id, value):
        return self.__update_user_info_by(id, 'profile_picture', value)

    def send_friend_request(self, user_id, friend_id):
        self.connect()
        cursor = self.connection.cursor(buffered=True, dictionary=True)

        query = """
            INSERT INTO user_friends (user_id, friend_id, status)
            VALUES (%s, %s, 'pending')
            ON DUPLICATE KEY UPDATE status = 'pending';
            """
        cursor.execute(query, (user_id, friend_id))
        self.connection.commit()
        cursor.close()
        self.disconnect()

    def confirm_friend_request(self, user_id, friend_id):
        self.connect()
        cursor = self.connection.cursor(buffered=True, dictionary=True)
        confirm_query = """
            UPDATE user_friends SET status = 'accepted'
            WHERE user_id = %s AND friend_id = %s;
            """
        cursor.execute(confirm_query, (user_id, friend_id))

        reciprocal_query = """
            INSERT INTO user_friends (user_id, friend_id, status)
            VALUES (%s, %s, 'accepted')
            ON DUPLICATE KEY UPDATE status = 'accepted';
            """
        cursor.execute(reciprocal_query, (friend_id, user_id))
        self.connection.commit()
        cursor.close()
        self.disconnect()

    def delete_friend(self, user_id, friend_id):
        self.connect()
        cursor = self.connection.cursor()
        query = """
                DELETE FROM user_friends
                WHERE (user_id = %s AND friend_id = %s)
                OR (user_id = %s AND friend_id = %s);
                """
        cursor.execute(query, (user_id, friend_id, friend_id, user_id))
        self.connection.commit()
        cursor.close()
        self.disconnect()

    def check_friendship_status(self, user_id, friend_id):
        self.connect()
        cursor = self.connection.cursor(buffered=True, dictionary=True)
        query = """
            SELECT status FROM user_friends
            WHERE (user_id = %s AND friend_id = %s)
            OR (user_id = %s AND friend_id = %s);
        """
        cursor.execute(query, (user_id, friend_id, friend_id, user_id))
        result = cursor.fetchone()
        return 'not_friends' if result is None else result['status']

    def check_pending_invites(self, user_id):
        self.connect()
        cursor = self.connection.cursor(dictionary=True)
        query = """
                SELECT users.user_id, users.username, users.profile_picture, users.status
                FROM user_friends
                JOIN users ON user_friends.user_id = users.user_id
                WHERE user_friends.friend_id = %s AND user_friends.status = 'pending';
                """
        cursor.execute(query, (user_id,))
        pending_invites = cursor.fetchall()
        cursor.close()
        self.disconnect()
        return pending_invites

    def get_all_friends(self, user_id):
        self.connect()
        cursor = self.connection.cursor(dictionary=True)
        query = """
                    SELECT users.user_id, users.username, users.profile_picture, users.status
                    FROM user_friends
                    JOIN users ON (user_friends.friend_id = users.user_id OR user_friends.user_id = users.user_id)
                    WHERE (user_friends.user_id = %s OR user_friends.friend_id = %s) AND user_friends.status = 'accepted'
                    AND users.user_id != %s;
                    """
        cursor.execute(query, (user_id, user_id, user_id))
        friends = cursor.fetchall()
        cursor.close()
        self.disconnect()
        return friends
