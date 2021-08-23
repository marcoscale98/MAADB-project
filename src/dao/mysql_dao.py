import sys
from typing import Union, List, Optional, Generator

import math
from mysql.connector.cursor import CursorBase

from src.dao.dao import DAO

import mysql.connector
from mysql.connector import errorcode, MySQLConnection, IntegrityError

from src.dao.utils.config import *
from src.dao.utils.nomi_db_emozioni import Nomi_db_mysql


class MySQLDAO(DAO):
    def __init__(self, url=None):
        super().__init__(url)

    def _connect(self, db: str = None, collezione: str = None):
        '''

        :param db: inutilizzato
        :param collezione: inutilizzato
        :return:
        '''
        try:
            cnx = mysql.connector.connect(**MYSQL_CONFIG)
            cnx.autocommit = True
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err, file=sys.stderr)
        else:
            return cnx

    def _disconnect(self, conn: MySQLConnection):
        conn.close()

    def upload_lemmi_of_lexres(self, emozione: str, lemmi, drop_if_not_empty: bool):
        conn: MySQLConnection = self._connect()
        cursor = conn.cursor()
        if drop_if_not_empty:
            self._drop_if_not_empty(cursor, Nomi_db_mysql.RISORSA_LESSICALE.value)
        parole_per_ris_les = []
        parole = []
        for lemma in lemmi:
            resources = lemma['res'].keys()
            parole.append((lemma['lemma'],))
            for res in resources:
                parole_per_ris_les.append((res, emozione, lemma['lemma']))
        self.insert_parole_in_ris_les(cursor, parole_per_ris_les)
        self.insert_parole(cursor, parole)
        self._disconnect(conn)
        return len(parole_per_ris_les)

    def insert_parole_in_ris_les(self, cursor, parole_per_ris_les):
        query = f'INSERT INTO {Nomi_db_mysql.RISORSA_LESSICALE.value} (risorsa, emozione, parola) VALUES (%s,%s,%s)'
        cursor.executemany(query, parole_per_ris_les)

    def chunk_by_size(self, lst: List, size: int):
        n = math.ceil(len(lst) / size)
        return list(map(lambda x: lst[x * size:x * size + size], list(range(n))))

    def upload_twitter_messages(self, emozione: str, messages: list, drop_if_not_empty: bool):
        conn: MySQLConnection = self._connect()
        # faccio upload dei messaggi twitter
        cursor = conn.cursor()
        chunkes = self.chunk_by_size(messages, 1000)
        if drop_if_not_empty:
            self._drop_if_not_empty(cursor, Nomi_db_mysql.MESSAGGIO_TWITTER.value)
        for chuck in chunkes:
            data = list(map(lambda message: (message, emozione), chuck))
            query = f"INSERT INTO {Nomi_db_mysql.MESSAGGIO_TWITTER.value} (messaggio,emozione) VALUES (%s,%s)"
            cursor.executemany(query, data)
        self._disconnect(conn)
        return len(messages)

    def upload_words(self, words: List[Union[str, dict]], emotion: str):
        query = f'INSERT INTO {Nomi_db_mysql.PAROLA_CONTENUTA.value} (parola,emozione) values (%s,%s)'
        self.upload_tokens(words, emotion, query)
    def upload_emoji(self, emoji, emotion):
        query=f'INSERT INTO {Nomi_db_mysql.EMOJI_CONTENUTA.value} (emoji,emozione) values (%s,%s)'
        self.upload_tokens(emoji, emotion, query)

    def upload_emoticons(self, emoticons, emotion):
        query=f'INSERT INTO {Nomi_db_mysql.EMOTICON_CONTENUTA.value} (emoticon,emozione) values (%s,%s)'
        self.upload_tokens(emoticons, emotion, query)

    def upload_hashtags(self, hashtags, emotion):
        query=f'INSERT INTO {Nomi_db_mysql.HASHTAG_CONTENUTO.value} (hashtag,emozione) values (%s,%s)'
        self.upload_tokens(hashtags, emotion,query)

    def upload_tokens(self,tokens,emotion, query):
        conn=self._connect()
        cursor=conn.cursor()
        tokens_upload= list(map(lambda token: (token,emotion), tokens))
        cursor.executemany(tokens,query)
    def _drop_if_not_empty(self, cursor: CursorBase, table: str):
        query = 'TRUNCATE ' + table
        cursor.execute(query)

    def insert_parole(self, cursor, parole):
        try:
            query = f'INSERT INTO {Nomi_db_mysql.PAROLA.value} (parola) VALUES (%s)'
            cursor.executemany(query, parole)
        except IntegrityError:
            pass

    def download_messaggi_twitter(self, emozione: Optional[str]) -> Generator:
        conn=self._connect()
        cursor=conn.cursor()
        query=f'SELECT * FROM {Nomi_db_mysql.MESSAGGIO_TWITTER.value}'
        if emozione is not None:
            query += " WHERE emozione=%s"
            data=(emozione,)
            cursor.execute(query,data)
        else:
            cursor.execute(query)
        for messaggio in cursor:
            yield messaggio
