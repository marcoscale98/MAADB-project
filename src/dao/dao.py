from typing import Union
from src.user_exception import InterfaceException

class DAO:
    """
    Questa è un interfaccia per parlare con il DB
    """
    def __init__(self,url):
        self.url=url
    def populate_db_lexres(self):
        '''
        carica su db il file delle lexical resouces
        :return:
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

    def populate_db_twitter(self):
        """
        popola il database dei messaggi twitter
        :return:
        """
        raise InterfaceException