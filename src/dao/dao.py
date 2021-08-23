from typing import Union, List, Optional, Generator

from pymongo.database import Database

from src.user_exception import interface_exceptions

class DAO:
    """
    Questa è un interfaccia per parlare con il DB
    """
    def __init__(self,url):
        self.url=url

    def _connect(self, db:str=None, collezione: str=None):
        raise interface_exceptions

    def _disconnect(self, db: Database):
        raise interface_exceptions

    def upload_lemmi_of_lexres(self, emozione:Union[str,None], lemmi, drop_if_not_empty: bool):
        '''
        carica i lemmi nel `lexres_db`
        :param emozione:
        :param lemmi:
        :return: numero di inserimenti
        '''
        raise interface_exceptions

    def upload_twitter_messages(self,emozione:str, messages, drop_if_not_empty: bool):
        '''
        carica i messaggi twitter nel database
        :param emozione:
        :param messages:
        :return: numero di inserimenti
        '''
        raise interface_exceptions

    def upload_words(self, words: List[Union[str, dict]], emotion: str, type: str = 'word'):
        """
        per fare upload di parole, hashtags, emoji, emoticons
        :param words:
        :param emotion:
        :param type:
        :return:
        """
        raise interface_exceptions

    def upload_emoji(self,emoji, emotion):
        raise interface_exceptions

    def upload_emoticons(self,emoticons, emotion):
        raise interface_exceptions

    def upload_hashtags(self,hashtags, emotion):
        raise interface_exceptions

    def download_messaggi_twitter(self,emozione:Optional[str])->Generator:
        '''
        generatore di messaggi twitter presi dal db
        '''
        raise interface_exceptions

