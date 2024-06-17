from mysql.connector import pooling
from flask import Flask


class DbConnection:
    def __init__(self, app: Flask):
        self.dbconfig = {
            'host': app.config['DB_HOST'],
            'database': app.config['DB_NAME'],
            'user': app.config['DB_USER'],
            'password': app.config['DB_PASS']
        }

        self.pool = pooling.MySQLConnectionPool(pool_size=10, **self.dbconfig)

    def connect(self):
        return self.pool.get_connection()

    def add_note(self, user_id, type):
        connection = self.connect()
        cursor = connection.cursor()

        query = '''
        INSERT INTO notes(user_id, type)
        VALUES(%s, %s)
        '''

        cursor.execute(query, (user_id, type))
        note_id = cursor.lastrowid
        connection.commit()
        cursor.close()
        connection.close()
        return note_id

    def add_post_detail(self, note_id, content, image_path):
        connection = self.connect()
        cursor = connection.cursor()

        query = '''
        INSERT INTO posts(note_id, content, image_path)
        VALUES (%s, %s, %s)'''

        cursor.execute(query, (note_id, content, image_path))
        connection.commit()
        cursor.close()
        connection.close()

    def add_recipe_detail(self, note_id, recipe_name,
                          ingredients, steps, image_path):
        connection = self.connect()
        cursor = connection.cursor()

        query = '''
        INSERT INTO recipes(note_id, recipe_name,
                            ingredients, steps, image_path)
        VALUES(%s, %s, %s, %s, %s)
        '''

        cursor.execute(query, (note_id, recipe_name,
                       ingredients, steps, image_path))
        connection.commit()
        cursor.close()
        connection.close()

    def add_video_recipe_detail(self, note_id, recipe_name, video_url):
        connection = self.connect()
        cursor = connection.cursor()

        query = '''
        INSERT INTO video_recipes(note_id, recipe_name, video_url)
        VALUES (%s, %s, %s)'''

        cursor.execute(query, (note_id, recipe_name, video_url))
        connection.commit()
        cursor.close()
        connection.close()

    def add_message(self, data):
        connection = self.connect()
        cursor = connection.cursor()

        query = '''
        INSERT INTO messages(sender_id, receiver_id, content, sent_at)
        VALUES(%s, %s, %s, %s)
        '''

        cursor.execute(query, data)
        connection.commit()
        cursor.close()
        connection.close()

    def add_like(self, user_id, note_id):
        connection = self.connect()
        cursor = connection.cursor()

        query = '''
        INSERT INTO likes(user_id, note_id) VALUES (%s, %s)
        '''

        cursor.execute(query, (user_id, note_id))
        connection.commit()
        cursor.close()
        connection.close()

    def add_comment(self, user_id, note_id, content):
        connection = self.connect()
        cursor = connection.cursor()

        query = '''
        INSERT INTO comments(user_id, note_id, content) VALUES (%s, %s, %s)
        '''

        cursor.execute(query, (user_id, note_id, content))
        connection.commit()
        cursor.close()
        connection.close()

    def get_comments_for_note(self, note_id):
        connection = self.connect()
        cursor = connection.cursor()

        query = '''
        SELECT users.username, users.profile_picture,
        comments.content, comments.created_at
        FROM comments
        INNER JOIN users ON comments.user_id = users.user_id
        WHERE comments.note_id = %s
        ORDER BY comments.created_at ASC
        '''

        cursor.execute(query, (note_id,))
        res = cursor.fetchall()
        cursor.close()
        connection.close()
        return res

    def remove_like(self, user_id, note_id):
        connection = self.connect()
        cursor = connection.cursor()

        query = '''
        DELETE FROM likes WHERE user_id = %s AND note_id = %s
        '''

        cursor.execute(query, (user_id, note_id))
        connection.commit()
        cursor.close()
        connection.close()

    def add_user(self, data):
        connection = self.connect()
        cursor = connection.cursor()

        query = '''
        INSERT INTO users(username, email, password_hash)
        VALUES(%s, %s, %s)
        '''

        cursor.execute(query, data)
        connection.commit()
        cursor.close()
        connection.close()

    def has_like(self, user_id, note_id):
        connection = self.connect()
        cursor = connection.cursor()

        query = '''
        SELECT COUNT(1)
        FROM likes
        WHERE user_id = %s AND note_id = %s
        '''

        cursor.execute(query, (user_id, note_id))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result[0] > 0

    def has_favorite(self, user_id, note_id):
        connection = self.connect()
        cursor = connection.cursor()

        query = '''
        SELECT COUNT(1)
        FROM favorites
        WHERE user_id = %s AND note_id = %s
        '''

        cursor.execute(query, (user_id, note_id))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result[0] > 0

    def add_favorite(self, user_id, note_id):
        connection = self.connect()
        cursor = connection.cursor()

        query = '''
        INSERT INTO favorites (user_id, note_id) VALUES (%s, %s)
        '''

        cursor.execute(query, (user_id, note_id))
        connection.commit()
        cursor.close()
        connection.close()

    def remove_favorite(self, user_id, note_id):
        connection = self.connect()
        cursor = connection.cursor()

        query = '''
        DELETE FROM favorites WHERE user_id = %s AND note_id = %s
        '''

        cursor.execute(query, (user_id, note_id))
        connection.commit()
        cursor.close()
        connection.close()

    def get_notes(self, user_id=None, notes=False,
                  likes=False, favorites=False):
        connection = self.connect()
        cursor = connection.cursor(dictionary=True)

        query = '''
        SELECT notes.*, users.username, users.profile_picture,
        (SELECT COUNT(DISTINCT likes.like_id)
        FROM likes
        WHERE likes.note_id = notes.note_id)
        AS like_count,
        (SELECT COUNT(DISTINCT comments.comment_id)
        FROM comments
        WHERE comments.note_id = notes.note_id)
        AS comment_count,
        (SELECT COUNT(DISTINCT favorites.favorite_id)
        FROM favorites
        WHERE favorites.note_id = notes.note_id)
        AS favorite_count
        FROM notes
        INNER JOIN users ON notes.user_id = users.user_id
        '''

        conditions = []
        params = []

        if user_id is not None:
            if notes:
                conditions.append('notes.user_id = %s')
                params.append(user_id)

            if likes:
                query += '''INNER JOIN likes
                            ON notes.note_id = likes.note_id '''
                conditions.append('likes.user_id = %s')
                params.append(user_id)

            if favorites:
                query += '''INNER JOIN favorites
                            ON notes.note_id = favorites.note_id '''
                conditions.append('favorites.user_id = %s')
                params.append(user_id)

        if conditions:
            query += 'WHERE ' + ' AND '.join(conditions)

        query += '''
        GROUP BY notes.note_id, users.username, users.profile_picture
        ORDER BY notes.created_at DESC
        '''

        cursor.execute(query, tuple(params))

        res = cursor.fetchall()
        cursor.close()
        connection.close()
        return res

    def get_post_info(self, id):
        connection = self.connect()
        cursor = connection.cursor(dictionary=True)

        query = '''
        SELECT posts.content, posts.image_path
        FROM notes
        LEFT JOIN posts ON notes.note_id = posts.note_id
        WHERE notes.type = 'post' AND notes.note_id = %s
        '''

        cursor.execute(query, (id, ))
        res = cursor.fetchone()
        cursor.close()
        connection.close()
        return res

    def get_recipe_info(self, id):
        connection = self.connect()
        cursor = connection.cursor(dictionary=True)

        query = '''
        SELECT recipes.recipe_name, recipes.ingredients,
        recipes.steps, recipes.image_path
        FROM notes
        LEFT JOIN recipes ON notes.note_id = recipes.note_id
        WHERE notes.type = 'recipe' AND notes.note_id = %s
        '''

        cursor.execute(query, (id, ))
        res = cursor.fetchone()
        cursor.close()
        connection.close()
        return res

    def get_video_recipe_info(self, id):
        connection = self.connect()
        cursor = connection.cursor(dictionary=True)

        query = '''
        SELECT video_recipes.recipe_name, video_recipes.video_url
        FROM notes
        LEFT JOIN video_recipes ON notes.note_id = video_recipes.note_id
        WHERE notes.type = 'video_recipe' AND notes.note_id = %s
        '''

        cursor.execute(query, (id, ))
        res = cursor.fetchone()
        cursor.close()
        connection.close()
        return res

    def get_messages_for_chat(self, user_id_1: int, user_id_2: int):
        connection = self.connect()
        cursor = connection.cursor(dictionary=True)

        query = '''
        SELECT m.message_id, m.sender_id,
        s.username AS sender_username,
        s.profile_picture AS sender_avatar,
        m.receiver_id,
        r.username AS receiver_username,
        r.profile_picture AS receiver_avatar,
        m.content, m.sent_at
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
        connection.close()
        return res

    def get_chats_for_user_by_id(self, user_id: int):
        connection = self.connect()
        cursor = connection.cursor(dictionary=True)

        query = '''
        SELECT u.username AS chat_partner_username,
        u.profile_picture AS chat_partner_avatar,
        m1.content AS last_message_text,
        m1.sent_at AS last_message_sent_at
        FROM messages m1
        INNER JOIN users u ON u.user_id = CASE
        WHEN m1.sender_id = %s THEN m1.receiver_id
        ELSE m1.sender_id
        END
        WHERE (m1.sender_id = %s OR m1.receiver_id = %s) AND m1.sent_at = (
        SELECT MAX(m2.sent_at)
        FROM messages m2
        WHERE
        (m2.sender_id=m1.sender_id AND m2.receiver_id=m1.receiver_id)
        OR(m2.sender_id=m1.receiver_id AND m2.receiver_id=m1.sender_id)
        )
        GROUP BY
        chat_partner_username,
        last_message_text,
        last_message_sent_at
        ORDER BY
        last_message_sent_at DESC;
        '''

        cursor.execute(query, (user_id, user_id, user_id))
        res = cursor.fetchall()
        cursor.close()
        connection.close()
        return res

    def __get_post_by(self, column_name, value):
        connection = self.connect()
        cursor = connection.cursor(buffered=True, dictionary=True)

        query = f'''
        SELECT *
        FROM posts
        WHERE {column_name} = %s
        '''

        cursor.execute(query, (value, ))
        res = cursor.fetchone()
        cursor.close()
        connection.close()
        return res

    def get_post_by_id(self, value):
        return self.__get_post_by('post_id', value)

    def __get_user_by(self, column_name, value):
        connection = self.connect()
        cursor = connection.cursor(buffered=True, dictionary=True)

        query = f'''
        SELECT *
        FROM users
        WHERE {column_name} = %s
        '''

        cursor.execute(query, (value, ))
        res = cursor.fetchone()
        cursor.close()
        connection.close()
        return res

    def get_user_by_username(self, value: str):
        return self.__get_user_by('username', value)

    def get_user_by_email(self, email: str):
        return self.__get_user_by('email', email)

    def get_user_by_id(self, value):
        return self.__get_user_by('user_id', value)

    def update_user_password(self, email, password):
        connection = self.connect()
        cursor = connection.cursor(buffered=True, dictionary=True)

        query = '''
        UPDATE users
        SET password_hash = %s
        WHERE email = %s
        '''

        values = (password, email)
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()

    def __update_user_info_by(self, id, column_name, value):
        connection = self.connect()
        cursor = connection.cursor(buffered=True, dictionary=True)

        query = f'''
        UPDATE users
        SET {column_name} = %s
        WHERE user_id = %s
        '''

        values = (value, id)
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()

    def update_user_username(self, id, value):
        return self.__update_user_info_by(id, 'username', value)

    def update_user_email(self, id, value):
        return self.__update_user_info_by(id, 'email', value)

    def update_user_status(self, id, value):
        return self.__update_user_info_by(id, 'status', value)

    def update_user_profile_picture(self, id, value):
        return self.__update_user_info_by(id, 'profile_picture', value)

    def send_friend_request(self, user_id: int, friend_id: int):
        """
        Отправка запроса в друзья и создания соответствующей записи в БД.
        """
        connection = self.connect()
        cursor = connection.cursor(buffered=True, dictionary=True)

        query = '''
        INSERT INTO user_friends(user_id, friend_id, status)
        VALUES (%s, %s, 'pending')
        ON DUPLICATE KEY UPDATE status = 'pending';
        '''

        cursor.execute(query, (user_id, friend_id))
        connection.commit()
        cursor.close()
        connection.close()

    def check_busy_nickname(self, nickname: str):
        """
        Проверка на наличие указанного ника.
        """
        connection = self.connect()
        cursor = connection.cursor(buffered=True, dictionary=True)

        query = '''
        SELECT username from users
        WHERE username = %s
        '''

        cursor.execute(query, (nickname, ))
        busy = cursor.fetchall()
        cursor.close()
        connection.close()
        return busy

    def confirm_friend_request(self, user_id: int, friend_id: int):
        connection = self.connect()
        cursor = connection.cursor(buffered=True, dictionary=True)

        confirm_query = '''
        UPDATE user_friends SET status = 'accepted'
        WHERE user_id = %s AND friend_id = %s;
        '''

        cursor.execute(confirm_query, (user_id, friend_id))

        reciprocal_query = '''
        INSERT INTO user_friends(user_id, friend_id, status)
        VALUES (%s, %s, 'accepted')
        ON DUPLICATE KEY UPDATE status = 'accepted';
        '''

        cursor.execute(reciprocal_query, (friend_id, user_id))
        connection.commit()
        cursor.close()
        connection.close()

    def delete_friend(self, user_id: int, friend_id: int):
        connection = self.connect()
        cursor = connection.cursor()

        query = '''
        DELETE FROM user_friends
        WHERE (user_id = %s AND friend_id = %s)
        OR (user_id = %s AND friend_id = %s);
        '''

        cursor.execute(query, (user_id, friend_id, friend_id, user_id))
        connection.commit()
        cursor.close()
        connection.close()

    def check_friendship_status(self, user_id: int, friend_id: int):
        connection = self.connect()
        cursor = connection.cursor(buffered=True, dictionary=True)

        query = '''
        SELECT status FROM user_friends
        WHERE (user_id = %s AND friend_id = %s)
        OR (user_id = %s AND friend_id = %s);
        '''

        cursor.execute(query, (user_id, friend_id, friend_id, user_id))
        result = cursor.fetchone()
        connection.close()
        return 'not_friends' if result is None else result['status']

    def check_pending_invites(self, user_id: int):
        connection = self.connect()
        cursor = connection.cursor(dictionary=True)

        query = '''
        SELECT users.user_id, users.username,
        users.profile_picture, users.status
        FROM user_friends
        JOIN users ON user_friends.user_id = users.user_id
        WHERE user_friends.friend_id = %s AND user_friends.status = 'pending';
        '''

        cursor.execute(query, (user_id,))
        pending_invites = cursor.fetchall()
        cursor.close()
        connection.close()
        return pending_invites

    def get_all_friends(self, user_id: int):
        """
        Получение списка друзей для пользователя с `id`, равным `user_id`
        """
        connection = self.connect()
        cursor = connection.cursor(dictionary=True)

        query = '''
        SELECT users.user_id, users.username,
        users.profile_picture, users.status
        FROM user_friends
        JOIN users ON(user_friends.friend_id=users.user_id
        OR user_friends.user_id=users.user_id)
        WHERE (user_friends.user_id = %s OR user_friends.friend_id = %s)
        AND user_friends.status = 'accepted'
        AND users.user_id != %s;
        '''

        cursor.execute(query, (user_id, user_id, user_id))
        friends = cursor.fetchall()
        cursor.close()
        connection.close()
        return friends
