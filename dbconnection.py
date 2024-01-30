import psycopg2
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

    def add_user(self, data):
        self.connect()
        cursor = self.connection.cursor()
        query = '''INSERT INTO users(username, email, password_hash)
                   VALUES(%s, %s, %s)'''
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()
        self.disconnect()

    def __get_user_by(self, column_name, value):
        self.connect()
        cursor = self.connection.cursor()

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

    def get_user_by_email(self, value):
        return self.__get_user_by('email', value)

    def get_user_by_id(self, value):
        return self.__get_user_by('user_id', value)
