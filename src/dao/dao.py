from typing import Union, List, Optional, Generator

from pymongo.database import Database

from src.dao import mongodb_dao, mysql_dao
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

    def _test_get_messaggi(dao):
        emozione = 'anger'
        gen = dao.download_messaggi_twitter(emozione)
        for mess in gen:
            print(mess)


if __name__ == '__main__':
    dao=mongodb_dao.MongoDBDAO(config.MONGO_CONFIG)
    dao=mysql_dao.MySQLDAO(config.MYSQL_CONFIG)
    dao.test_connessione()
    dao._test_insert_parola()
    dao._test_insert_emoji()
    dao._test_insert_emoticon()
    dao._test_insert_hashtag()
    dao._test_get_messaggi()


