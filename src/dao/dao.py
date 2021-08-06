from typing import Union
from src.user_exception import InterfaceException

class DAO:
    """
    Questa è un interfaccia per parlare con il DB
    """
    def __init__(self,url):
        self.url=url

    def drop_collection(self, db, coll):
        raise InterfaceException

    def upload_lemmi_of_lexres(self, emozione:str, lemmi):
        '''
        carica i lemmi nel `lexres_db`
        :param emozione:
        :param lemmi:
        :return: numero di inserimenti
        '''
        raise InterfaceException

    def upload_twitter_messages(self,emozione:str, messages):
        '''
        carica i messaggi twitter nel database
        :param emozione:
        :param messages:
        :return: numero di inserimenti
        '''
        raise InterfaceException

    def upload_words(self,words: list[Union[str,dict]], emotion: str, type: str = 'word'):
        """
        per fare upload di parole, hashtags, emoji, emoticons
        :param words:
        :param emotion:
        :param type:
        :return:
        """
        raise InterfaceException

    def upload_emoji(self,emoji, emotion):
        raise InterfaceException

    def upload_emoticons(self,emoticons, emotion):
        raise InterfaceException

    def upload_hashtags(self,hashtags, emotion):
        raise InterfaceException

    def drop_if_not_empty(self, db:str, emozione:str):
        raise InterfaceException
