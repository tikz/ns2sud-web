import pymysql.cursors

from app import app


class Database():
    def __enter__(self):
        self.conn = pymysql.connect(host=app.config['NS2PLUS_MYSQL_HOST'], user=app.config['NS2PLUS_MYSQL_USER'],
                                    passwd=app.config['NS2PLUS_MYSQL_PASS'], db=app.config['NS2PLUS_MYSQL_DB'])
        self.cursor = self.conn.cursor()
        return self

    def execute(self, query, params=None):
        class Wrapper():
            def __init__(self, cursor, query):
                self.cursor = cursor
                self.cursor.execute(query, params)

            def fetchall(self):
                columns = [col[0] for col in self.cursor.description]
                return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

            def fetchone(self):
                return self.cursor.fetchone()[0]

        return Wrapper(self.cursor, query)

    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()
