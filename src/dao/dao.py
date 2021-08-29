from pprint import pprint
from typing import Union, List, Optional, Generator

from pymongo.database import Database

from src.user_exception.interface_exceptions import InterfaceException
from src.utils import config


class DAO:
    """
    Questa è un interfaccia per parlare con il DB
    """
    def __init__(self,url):
        self.url=url

    def _connect(self, db:str=None, collezione: str=None):
        raise InterfaceException

    def _disconnect(self, db: Database):
        raise InterfaceException

    def upload_lemmi_of_lexres(self, emozione:Union[str,None], lemmi, drop_if_not_empty: bool):
        '''
        carica i lemmi nel `lexres_db`
        :param emozione:
        :param lemmi:
        :return: numero di inserimenti
        '''
        raise InterfaceException

    def upload_twitter_messages(self,emozione:str, messages, drop_if_not_empty: bool):
        '''
        carica i messaggi twitter nel database
        :param emozione:
        :param messages:
        :return: numero di inserimenti
        '''
        raise InterfaceException

    def upload_words(self, words: List[Union[str, dict]], emotion: str)-> int:
        """
        per fare upload di parole, hashtags, emoji, emoticons
        :param words:
        :param emotion:
        :param type:
        :return:
        """
        raise InterfaceException

    def upload_emoji(self,emoji, emotion)->int:
        raise InterfaceException

    def upload_emoticons(self,emoticons, emotion)->int:
        raise InterfaceException

    def upload_hashtags(self,hashtags, emotion)->int:
        raise InterfaceException

    def download_messaggi_twitter(self,emozione:Optional[str],limit:int=None)->Generator:
        '''
        generatore di messaggi twitter presi dal db
        '''
        raise InterfaceException

    def test_connessione(self):
        raise InterfaceException

    def download_emojis(self,emozione)->dict:
        '''

        :return: dict=<token,quantita>
        '''
        raise InterfaceException

    def download_emoticons(self,emozione)-> dict:
        '''

        :return: dict=<token,quantita>
        '''
        raise InterfaceException

    def download_parole(self,emozione)-> dict:
        '''

        :return: dict=<token,quantita>
        '''
        raise InterfaceException

    def download_hashtags(self,emozione)-> dict:
        '''

        :return: dict=<token,quantita>
        '''
        raise InterfaceException

    def _test_insert_parola(dao):
        res = dao.upload_words(["parola"], "anger")
        print(f"Inserito {res} parole")

    def _test_insert_hashtag(dao):
        res = dao.upload_hashtags(["#hashtag"], 'anger')
        print(f"Inserito {res} hashtags")

    def _test_insert_emoji(dao):
        res = dao.upload_emoji(['😀'], 'anger')
        print(f'Inseriti {res} emoji')

    def _test_insert_emoticon(dao):
        res = dao.upload_emoticons([':)'], 'anger')
        print(f'Inseriti {res} emoticon')


    def _test_download_messaggi(self):
        messaggi = self.download_messaggi_twitter('anger', 10)
        pprint(list(messaggi))

    def _test_download_tutti_messaggi(self):
        messaggi = self.download_messaggi_twitter('anger')
        pprint(f"Messaggi scaricati {len(list(messaggi))}")


if __name__ == '__main__':
    from src.dao.mongodb_dao import MongoDBDAO
    from src.dao.mysql_dao import MySQLDAO

    # dao=MongoDBDAO(config.MONGO_CONFIG)
    dao=MySQLDAO(config.MYSQL_CONFIG)
    # dao.test_connessione()
    # dao._test_download_messaggi()
    # dao._test_insert_parola()
    # dao._test_insert_emoji()
    # dao._test_insert_emoticon()
    # dao._test_insert_hashtag()

    emojis = dao.download_emojis('anger', limit=10)
    emoticons = dao.download_emoticons('anger', limit=10)
    parole = dao.download_parole('anger', limit=10)
    hashtags = dao.download_hashtags('anger', limit=10)
    pprint(emojis, indent=2)
    pprint(emoticons, indent=2)
    pprint(parole, indent=2)
    pprint(hashtags, indent=2)


