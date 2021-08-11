import sys
from typing import Union, List

import math
from mysql.connector.cursor import CursorBase
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
            cnx.autocommit=True
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

    def upload_lemmi_of_lexres(self, emozione: str, lemmi, drop_if_not_empty:bool):
        conn:MySQLConnection=self._connect()
        cursor=conn.cursor()
        if drop_if_not_empty:
            self._drop_if_not_empty(cursor,"risorsa_lessicale")
        query='INSERT INTO risorsa_lessicale (risorsa, emozione, parola) VALUES (%s,%s,%s)'
        lemmi_map=[]
        for lemma in lemmi:
            resources = lemma['res'].keys()
            for res in resources:
                lemmi_map.append((res,emozione,lemma['lemma']))
        cursor.executemany(query,lemmi_map)
        self._disconnect(conn)
        return len(lemmi_map)

    def chunk_by_size(self,lst:List, size:int):
            n = math.ceil(len(lst) / size)
            return list(map(lambda x: lst[x * size:x * size + size], list(range(n))))

    def upload_twitter_messages(self, emozione: str, messages:list, drop_if_not_empty:bool):
        conn:MySQLConnection= self._connect()
        #faccio upload dei messaggi twitter
        cursor=conn.cursor()
        chunkes= self.chunk_by_size(messages, 1000)
        if drop_if_not_empty:
            self._drop_if_not_empty(cursor, "messaggio_twitter")
        for chuck in chunkes:
            data = list(map(lambda message: (message, emozione), chuck))
            query="INSERT INTO messaggio_twitter (messaggio,emozione) VALUES (%s,%s)"
            cursor.executemany(query,data)
        self._disconnect(conn)
        return len(messages)

    def upload_words(self, words: List[Union[str, dict]], emotion: str, type: str = 'word'):
        return super().upload_words(words, emotion, type)

    def upload_emoji(self, emoji, emotion):
        return super().upload_emoji(emoji, emotion)

    def upload_emoticons(self, emoticons, emotion):
        return super().upload_emoticons(emoticons, emotion)

    def upload_hashtags(self, hashtags, emotion):
        return super().upload_hashtags(hashtags, emotion)

    def _drop_if_not_empty(self, cursor: CursorBase, table: str):
        query='TRUNCATE ' + table
        cursor.execute(query)
