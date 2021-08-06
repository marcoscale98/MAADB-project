import os
from typing import Union

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from impostazioni import *
from src.dao.dao import DAO

from src.dao.nomi_db_emozioni import Nomi_db, Emotions

class MongoDBDAO(DAO):

    def __init__(self, url):
        self.url=url

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

    def drop_collection(self, db, coll):
        database = self._connect(db)
        database.drop_collection(coll)
        self._disconnect(database)

    def upload_lemmi_of_lexres(self, emozione:str, lemmi):
        lex_res_db = self._connect(Nomi_db.LEX_RES_DB.value)
        num = lex_res_db[emozione].insert_many(lemmi)
        print(f'N. documenti inseriti nella collezione {lex_res_db[emozione].name}: {len(num.inserted_ids)}')
        print(f'n. documenti presenti nella collezione {lex_res_db[emozione].name}: {lex_res_db[emozione].count_documents({})}')
        self._disconnect(lex_res_db)
        return num.inserted_ids

    def upload_twitter_messages(self,emozione:str, messages):
        twitter_db = self._connect(Nomi_db.BUFFER_TWITTER_MESSAGES.value)
        num = twitter_db[emozione].insert_many(messages)
        print(f'N. documenti inseriti nella collezione {twitter_db[emozione].name}: {len(num.inserted_ids)}')
        print(f'n. documenti presenti nella collezione {twitter_db[emozione].name}: {twitter_db[emozione].count_documents({})}')
        self._disconnect(twitter_db)
        return num.inserted_ids

    def upload_words(self,words: list[Union[str,dict]], emotion: str, _type: str = 'word'):
        twitter_words_db = self._connect(Nomi_db.TWITTER_WORDS.value)
        emot_coll: Collection = twitter_words_db[emotion]
        if _type not in ("word", 'hashtag', 'emoji', 'emoticon'):
            raise Exception('_type not in ("word","hashtag","emoji","emoticon")')

        words = list(map(lambda word: self._add_type(word, _type), words))
        result = emot_coll[emotion].insert_many(words)
        if DEBUG:
            print(f'Inseriti {len(result.inserted_ids)} {_type} in {twitter_words_db.name}.{emot_coll.name}')
        self._disconnect(twitter_words_db)

    def _add_type(self,word, tipo):
        if type(word)==str:
            word= {
                'token':word,
                'type':tipo,
            }
        else:
            word['_type'] = tipo
        return word

    def upload_emoji(self,emoji, emotion):
        self.upload_words(emoji, emotion, "emoji")

    def upload_emoticons(self,emoticons, emotion):
        self.upload_words(emoticons, emotion, "emoticon")

    def upload_hashtags(self,hashtags, emotion):
        self.upload_words(hashtags, emotion, 'hashtag')

    def drop_words_collection(self,emotion):
        words_db = self._connect(Nomi_db.TWITTER_WORDS.value)
        words_coll = words_db[emotion]
        words_coll.drop()
        self._disconnect(words_db)

    def drop_if_not_empty(self, db: str, emozione: str):
        database = self._connect(db)
        emot_coll = database[emozione]
        if emot_coll.count_documents({}) > 0:
            emot_coll.drop()
        self._disconnect(database)


if __name__ == '__main__':
    mongodb_dao = MongoDBDAO("mongodb+srv://admin:admin@cluster0.9ajjj.mongodb.net/")
    # mongodb_dao.populate_db_twitter()
    mongodb_dao.populate_db_lexres()