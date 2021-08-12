import os
from typing import Union, Optional, Generator

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from impostazioni import *
from src.dao.dao import DAO

from src.dao.nomi_db_emozioni import Nomi_db_mongo, Emotions

class MongoDBDAO(DAO):

    def __init__(self, url):
        super().__init__(url)

    def _connect(self, db:str):
        '''
        si collega al database e restituisce l'oggetto
        :param db:
        :return:
        '''
        client =MongoClient(self.url + db+ "?retryWrites=true&w=majority")
        return client[db]

    def _disconnect(self,db:Database):
        '''
        si disconnette dal client mongo
        :param db:
        :return:
        '''
        db.client.close()

    def upload_lemmi_of_lexres(self, emozione:str, lemmi, drop_if_not_empty:bool):
        lex_res_db = self._connect(Nomi_db_mongo.RISORSA_LESSICALE.value)
        if drop_if_not_empty:
            self.drop_if_not_empty(Nomi_db_mongo.RISORSA_LESSICALE.value, emozione)
        num = lex_res_db[emozione].insert_many(lemmi)
        self._disconnect(lex_res_db)
        return len(num.inserted_ids)

    def upload_twitter_messages(self,emozione:str, messages, drop_if_not_empty:bool):
        messages = list(map(lambda m: {"message": m}, messages))
        twitter_db = self._connect(Nomi_db_mongo.MESSAGGIO_TWITTER.value)
        if drop_if_not_empty:
            self.drop_if_not_empty(Nomi_db_mongo.RISORSA_LESSICALE.value, emozione)
        num = twitter_db[emozione].insert_many(messages)
        self._disconnect(twitter_db)
        return len(num.inserted_ids)

    def upload_words(self, words: list[Union[str,dict]], emotion: str, tipo: str = 'word', drop_if_not_empty: bool =False):
        twitter_words_db = self._connect(Nomi_db_mongo.TOKEN_TWITTER.value)
        if drop_if_not_empty:
            self.drop_if_not_empty(Nomi_db_mongo.TOKEN_TWITTER.value, emotion)
        emot_coll: Collection = twitter_words_db[emotion]
        if tipo not in ("word", 'hashtag', 'emoji', 'emoticon'):
            raise Exception('tipo not in ("word","hashtag","emoji","emoticon")')

        words = list(map(lambda word: self._add_type(word, tipo), words))
        risultati = emot_coll[emotion].insert_many(words)
        self._disconnect(twitter_words_db)
        return len(risultati)

    def _add_type(self,word, tipo):
        if type(word)==str:
            word= {
                'token':word,
                'tipo':tipo,
            }
        else:
            word['tipo'] = tipo
        return word

    def upload_emoji(self,emoji, emotion):
        return self.upload_words(emoji, emotion, "emoji")

    def upload_emoticons(self,emoticons, emotion):
        return self.upload_words(emoticons, emotion, "emoticon")

    def upload_hashtags(self,hashtags, emotion):
        return self.upload_words(hashtags, emotion, 'hashtag')

    def drop_words_collection(self,emotion):
        words_db = self._connect(Nomi_db_mongo.TOKEN_TWITTER.value)
        words_coll = words_db[emotion]
        words_coll.drop()
        self._disconnect(words_db)

    def drop_if_not_empty(self, db: str, emozione: str):
        database = self._connect(db)
        emot_coll = database[emozione]
        if emot_coll.count_documents({}) > 0:
            emot_coll.drop()
        self._disconnect(database)

    def download_messaggi_twitter(self, emozione: Optional[str]='anger') -> Generator:
        min = 0
        max = 100
        while True:
            db = self._connect(Nomi_db_mongo.MESSAGGIO_TWITTER.value)
            emozione_coll=db[emozione]
            cursor=emozione_coll.find()[min:max]
            messaggi = list(cursor)
            self._disconnect(db)
            min += 100
            max += 100
            if len(messaggi)==0:
                print("Messaggi finiti")
                return
            for mess in messaggi:
                yield mess


if __name__ == '__main__':
    pass
    # mongodb_dao = MongoDBDAO("mongodb+srv://admin:admin@cluster0.9ajjj.mongodb.net/")
    # mongodb_dao.populate_db_twitter()
    # mongodb_dao.populate_db_lexres()