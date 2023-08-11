import sqlite3
import time
import re

from flask import url_for

class DataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def get_menu(self):
        sql = 'SELECT * FROM mainmenu'
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except IOError:
            print('Ошибка чтения базы данных')
        return []

    def add_post(self, title, text, url):
        try:
            self.__cur.execute('SELECT COUNT() as "count" FROM posts WHERE url LIKE ?', (url,))
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print('Статья с таким url уже существует!')
                return False

            base = url_for('static', filename='images')
            text = re.sub(r'(?P<tag><img\s+[^>]*src=)(?P<quote>[\'"])(?P<url>.*)(?P=quote)>',
                          r'\g<tag>' + base + r'/\g<url>>', text)

            tm = int(time.time())
            self.__cur.execute('INSERT INTO posts VALUES(NULL, ?, ?, ?, ?)', (title, text, url,
                                                                              tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка добавления статьи в базу данных' + str(e))
            return False
        return True

    def get_posts_announces(self):
        try:
            self.__cur.execute('SELECT id, title, text, url FROM posts ORDER BY time DESC')
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print('Ошибка получения статьи из базы данных' + str(e))
        return []

    def get_post(self, post_id):
        try:
            self.__cur.execute(f'SELECT title, text FROM posts WHERE url == "{post_id}"')
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print('Ошибка получения статьи из базы данных' + str(e))
        return None, None