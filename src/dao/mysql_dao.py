import sys
from pprint import pprint
from typing import Union, List, Optional, Generator

import math
from mysql.connector.cursor import CursorBase

from src.dao.dao import DAO

import mysql.connector
from mysql.connector import errorcode, MySQLConnection, IntegrityError

from src.utils.config import MYSQL_CONFIG
from src.utils.nomi_db_emozioni import Nomi_db_mysql, Risorse


class MySQLDAO(DAO):
    def __init__(self, url=None):
        '''
        url è un dizionario di configurazione
        es. {
                'user':str,
                'password':str,
                'host':str,
                'database': str,
            }
        '''
        self.url=url

    def _connect(self, db: str = None, collezione: str = None):
        '''

        :param db: inutilizzato
        :param collezione: inutilizzato
        :return:
        '''
        try:
            cnx = mysql.connector.connect(**self.url)
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
            self._drop_if_not_empty(cursor, Nomi_db_mysql.RISORSA_LESSICALE.value, emozione)
        parole_per_ris_les = []
        parole = []
        for lemma in lemmi:
            resources = lemma['risorse'].keys()
            parole.append((lemma['lemma'],))
            for res in resources:
                parole_per_ris_les.append((res, emozione, lemma['lemma']))
        self._insert_parole_in_ris_les(cursor, parole_per_ris_les)
        self._insert_parole(cursor, parole)
        self._disconnect(conn)
        return len(parole_per_ris_les)

    def _insert_parole_in_ris_les(self, cursor, parole_per_ris_les):
        query = f'INSERT INTO {Nomi_db_mysql.RISORSA_LESSICALE.value} (risorsa, emozione, parola) VALUES (%s,%s,%s)'
        cursor.executemany(query, parole_per_ris_les)

    def _chunk_by_size(self, lst: List, size: int):
        n = math.ceil(len(lst) / size)
        return list(map(lambda x: lst[x * size:x * size + size], list(range(n))))

    def upload_twitter_messages(self, emozione: str, messages: list, drop_if_not_empty: bool=False):
        conn: MySQLConnection = self._connect()
        # faccio upload dei messaggi twitter
        cursor = conn.cursor()
        chunkes = self._chunk_by_size(messages, 1000)
        if drop_if_not_empty:
            self._drop_if_not_empty(cursor, Nomi_db_mysql.MESSAGGIO_TWITTER.value, emozione)
        for chuck in chunkes:
            data = list(map(lambda message: (message, emozione), chuck))
            query = f"INSERT INTO {Nomi_db_mysql.MESSAGGIO_TWITTER.value} (messaggio,emozione) VALUES (%s,%s)"
            cursor.executemany(query, data)
        self._disconnect(conn)
        return len(messages)

    def upload_words(self, words: List[Union[str, dict]], emotion: str):
        if len(words)==0: return 0
        query = f'INSERT IGNORE INTO {Nomi_db_mysql.PAROLA_CONTENUTA.value} (parola,emozione,quantita) values (%s,%s,%s)'
        self._upload_tokens(words, emotion, query)

        query=f'INSERT IGNORE INTO {Nomi_db_mysql.PAROLA.value} (parola) values (%s)'
        conn=self._connect()
        cursor=conn.cursor()
        cursor.executemany(query,[(word,) for word in words])
        self._disconnect(conn)
        return len(words)

    def upload_emoji(self, emoji, emotion):
        if len(emoji)==0: return 0
        query=f'INSERT INTO {Nomi_db_mysql.EMOJI_CONTENUTA.value} (emoji,emozione,quantita) values (%s,%s,%s)'
        self._upload_tokens(emoji, emotion, query)
        return len(emoji)

    def upload_emoticons(self, emoticons, emotion):
        if len(emoticons)==0: return 0
        query=f'INSERT INTO {Nomi_db_mysql.EMOTICON_CONTENUTA.value} (emoticon,emozione,quantita) values (%s,%s,%s)'
        self._upload_tokens(emoticons, emotion, query)
        return len(emoticons)

    def upload_hashtags(self, hashtags, emotion):
        if len(hashtags)==0: return 0
        query=f'INSERT INTO {Nomi_db_mysql.HASHTAG_CONTENUTO.value} (hashtag,emozione,quantita) values (%s,%s,%s)'
        self._upload_tokens(hashtags, emotion, query)
        return len(hashtags)

    def _upload_tokens(self, tokens: Union[List,dict], emotion,query):
        conn=self._connect()
        cursor=conn.cursor()
        if type(tokens)==list:
            d=dict()
            for t in tokens:
                d[t]=1
            tokens=d
        tokens_upload= list(map(lambda item: (item[0],emotion, item[1]), tokens.items()))
        cursor.executemany(query, tokens_upload)
        return len(tokens)

    def _drop_if_not_empty(self, cursor: CursorBase, table: str, emozione:str=None):
        query = 'delete from ' + table + ' where emozione=\'' + emozione +"'"
        cursor.execute(query)

    def _insert_parole(self, cursor, parole):
        try:
            query = f'INSERT INTO {Nomi_db_mysql.PAROLA.value} (parola) VALUES (%s)'
            cursor.executemany(query, parole)
        except IntegrityError:
            pass

    def download_messaggi_twitter(self, emozione: Optional[str], limit:int=None) -> Generator:
        conn=self._connect()
        cursor=conn.cursor()
        query=f'SELECT * FROM {Nomi_db_mysql.MESSAGGIO_TWITTER.value}'
        if emozione is not None:
            query += f" WHERE emozione='{emozione}'"
        if limit is not None:
            query += f" LIMIT {limit}"
        cursor.execute(query)
        for messaggio in cursor:
            mess={
                'id':messaggio[0],
                'message':messaggio[1]
            }
            yield mess

    def test_connessione(self):
        conn=self._connect()
        self._disconnect(conn)
        print("Connessione effettuata con successo")

    def upload_nuove_parole_tweets(self, parole, emozione):
        conn=self._connect(Nomi_db_mysql.RISORSA_LESSICALE.value,emozione)
        cursor=conn.cursor()
        query=f'INSERT IGNORE INTO {Nomi_db_mysql.RISORSA_LESSICALE.value} (parola,emozione,risorsa) values (%s,%s,%s)'
        data=[(parola,emozione,Risorse.nuova_risorsa.value) for parola in parole]
        cursor.executemany(query,data)
        self._disconnect(conn)
        return len(parole)


    def download_parole_risorse_lessicali(self, emozione, risorsa=None):
        conn=self._connect()
        cursor=conn.cursor()
        query=f"select parola from {Nomi_db_mysql.RISORSA_LESSICALE.value} where emozione='{emozione}'"
        if risorsa:
            query+=f" and risorsa='{risorsa}'"
        cursor.execute(query)
        parole=cursor.fetchall()
        self._disconnect(conn)
        parole=list(parola[0] for parola in parole)
        return parole

    def download_emojis(self, emozione,limit:int=None) -> dict:
        conn=self._connect()
        cursor=conn.cursor()
        query=f'SELECT * FROM {Nomi_db_mysql.EMOJI_CONTENUTA.value}'
        if emozione is not None:
            query += f" WHERE emozione='{emozione}'"
        if limit:
            query += f" LIMIT {limit}"
        cursor.execute(query)
        res={}
        for obj in cursor:
            res[obj[0]]=obj[2]
        return res

    def download_emoticons(self, emozione,limit:int=None) -> dict:
        conn=self._connect()
        cursor=conn.cursor()
        query=f'SELECT * FROM {Nomi_db_mysql.EMOTICON_CONTENUTA.value}'
        if emozione is not None:
            query += f" WHERE emozione='{emozione}'"
        if limit:
            query += f" LIMIT {limit}"
        cursor.execute(query)
        res={}
        for obj in cursor:
            res[obj[0]]=obj[2]
        return res

    def download_parole_tweets(self, emozione, limit:int=None) -> dict:
        conn=self._connect()
        cursor=conn.cursor()
        query=f'SELECT * FROM {Nomi_db_mysql.PAROLA_CONTENUTA.value}'
        if emozione is not None:
            query += f" WHERE emozione='{emozione}'"
        if limit:
            query += f" LIMIT {limit}"
        cursor.execute(query)
        res={}
        for obj in cursor:
            res[obj[0]]=obj[2]
        return res

    def download_hashtags(self, emozione,limit:int=None) -> dict:
        conn=self._connect()
        cursor=conn.cursor()
        query=f'SELECT * FROM {Nomi_db_mysql.HASHTAG_CONTENUTO.value}'
        if emozione is not None:
            query += f" WHERE emozione='{emozione}'"
        if limit:
            query += f" LIMIT {limit}"
        cursor.execute(query)
        res={}
        for obj in cursor:
            res[obj[0]]=obj[2]
        return res

    def clear_databases(self):
        for table in Nomi_db_mysql:
            table=table.value
            conn=self._connect()
            cursor = conn.cursor()
            cursor.execute(f"TRUNCATE TABLE {table}")
            self._disconnect(conn)

    def _test_insert_parola(dao):
        super()._test_insert_parola()

    def _test_insert_hashtag(dao):
        super()._test_insert_hashtag()

    def _test_insert_emoji(dao):
        super()._test_insert_emoji()

    def _test_insert_emoticon(dao):
        super()._test_insert_emoticon()