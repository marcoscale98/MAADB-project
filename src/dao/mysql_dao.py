import sys
from typing import Union

from pymongo.database import Database

from src.dao.dao import DAO

import mysql.connector
from mysql.connector import errorcode, MySQLConnection

from src.config import *

class MySQLDAO(DAO):
    def __init__(self, url=None):
        super().__init__(url)

    def _connect(self, db: str=None, collezione: str=None):
        '''

        :param db: inutilizzato
        :param collezione: inutilizzato
        :return:
        '''
        try:
            cnx = mysql.connector.connect(**MYSQL_CONFIG)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err,file=sys.stderr)
        else:
            return cnx

    def _disconnect(self, conn: MySQLConnection):
        conn.close()

    def drop_collection(self, db, coll):
        '''

        :param db:
        :param coll:
        :return:
        '''
        return super().drop_collection(db, coll)

    def upload_lemmi_of_lexres(self, emozione: str, lemmi):
        conn:MySQLConnection=self._connect()
        print(conn)
        self._disconnect(conn)

    def upload_twitter_messages(self, emozione: str, messages):
        return super().upload_twitter_messages(emozione, messages)

    def upload_words(self, words: list[Union[str, dict]], emotion: str, type: str = 'word'):
        return super().upload_words(words, emotion, type)

    def upload_emoji(self, emoji, emotion):
        return super().upload_emoji(emoji, emotion)

    def upload_emoticons(self, emoticons, emotion):
        return super().upload_emoticons(emoticons, emotion)

    def upload_hashtags(self, hashtags, emotion):
        return super().upload_hashtags(hashtags, emotion)

    def drop_if_not_empty(self, db: str, emozione: str):
        return super().drop_if_not_empty(db, emozione)

if __name__ == '__main__':
    dao = MySQLDAO()
    dao.upload_lemmi_of_lexres(None,None)
