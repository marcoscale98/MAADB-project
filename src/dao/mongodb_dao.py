from pprint import pprint
from typing import Union, Optional, Generator

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.results import InsertManyResult

from src.dao.dao import DAO

from src.utils.nomi_db_emozioni import Nomi_db_mongo


class MongoDBDAO(DAO):

    def __init__(self, url):
        super().__init__(url)
        self.url=url

    def _connect(self, db:str=None, collezione:str=None)->Union[Database,Collection]:
        '''
        si collega al database e restituisce l'oggetto
        :param db:
        :param collezione:
        :return:
        '''
        client =MongoClient(**self.url)
        if collezione:
            return client[db][collezione]
        else:
            return client[db]

    def _disconnect(self,conn:Union[Database,Collection]):
        '''
        si disconnette dal client mongo
        :param db:
        :return:
        '''
        if type(conn)==Collection:
            db=conn.database
        elif type(conn)==Database:
            db=conn
        else:
            raise Exception('per disconnetermi dal MongoDB devi passare come parametro o il puntatore al db o ad una collezione')
        db.client.close()

    def upload_lemmi_of_lexres(self, emozione:str, lemmi, drop_if_not_empty:bool):
        lex_res_db = self._connect(Nomi_db_mongo.RISORSA_LESSICALE.value)
        if drop_if_not_empty:
            self._drop_if_not_empty(Nomi_db_mongo.RISORSA_LESSICALE.value, emozione)
        num = lex_res_db[emozione].insert_many(lemmi)
        self._disconnect(lex_res_db)
        return len(num.inserted_ids)

    def upload_twitter_messages(self,emozione:str, messages, drop_if_not_empty:bool):
        messages = list(map(lambda m: {"message": m}, messages))
        twitter_db = self._connect(Nomi_db_mongo.MESSAGGIO_TWITTER.value)
        if drop_if_not_empty:
            self._drop_if_not_empty(Nomi_db_mongo.MESSAGGIO_TWITTER.value, emozione)
        num = twitter_db[emozione].insert_many(messages)
        self._disconnect(twitter_db)
        return len(num.inserted_ids)

    def _upload_tokens(self, tokens: list[Union[str, dict]], emotion: str, tipo: str = 'parola', drop_if_not_empty: bool =False):
        twitter_words_db = self._connect(Nomi_db_mongo.TOKEN_TWITTER.value)
        if drop_if_not_empty:
            self._drop_if_not_empty(Nomi_db_mongo.TOKEN_TWITTER.value, emotion)
        emot_coll: Collection = twitter_words_db[emotion]
        if tipo not in ("parola", 'hashtag', 'emoji', 'emoticon'):
            raise Exception('tipo not in ("parola","hashtag","emoji","emoticon")')
        tokens = list(map(lambda token: self._add_type(token, tipo), tokens))
        risultati :InsertManyResult = emot_coll.insert_many(tokens)
        self._disconnect(twitter_words_db)
        return len(risultati.inserted_ids)

    def _add_type(self,parola, tipo):
        if type(parola)==str:
            parola= {
                'token':parola,
                'tipo':tipo,
            }
        else:
            parola['tipo'] = tipo
        return parola

    def upload_words(self, words: list[Union[str,dict]], emotion: str, drop_if_not_empty: bool =False):
        if len(words)==0: return 0
        return self._upload_tokens(words, emotion, "parola")

    def upload_emoji(self,emoji, emotion,drop_if_not_empty: bool =False):
        if len(emoji)==0: return 0
        return self._upload_tokens(emoji, emotion, "emoji")

    def upload_emoticons(self,emoticons, emotion,drop_if_not_empty: bool =False):
        if len(emoticons)==0: return 0
        return self._upload_tokens(emoticons, emotion, "emoticon")

    def upload_hashtags(self,hashtags, emotion,drop_if_not_empty: bool =False):
        if len(hashtags)==0: return 0
        return self._upload_tokens(hashtags, emotion, 'hashtag')

    def _drop_words_collection(self, emotion):
        words_db = self._connect(Nomi_db_mongo.TOKEN_TWITTER.value)
        words_coll = words_db[emotion]
        words_coll.drop()
        self._disconnect(words_db)

    def _drop_if_not_empty(self, db: str, emozione: str):
        emot_coll = self._connect(db,emozione)
        count=emot_coll.count_documents({})
        if count > 0:
            emot_coll.drop()
        self._disconnect(emot_coll)

    def download_messaggi_twitter(self, emozione: Optional[str]='anger',limit:int=None) -> Generator:
        min = 0
        max = 100
        if limit is not None:
            cond= (lambda : min<limit)
        else:
            cond=(lambda : True)
        while cond():
            if limit and max>limit:
                max=limit
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

    def test_connessione(self):
        conn=self._connect("test","test")
        self._disconnect(conn)
        return True
    def _test_download_messaggi(self):
        messaggi=self.download_messaggi_twitter('anger',10)
        pprint(list(messaggi))
    def _test_download_tutti_messaggi(self):
        messaggi=self.download_messaggi_twitter('anger')
        pprint(f"Messaggi scaricati {len(list(messaggi))}")

    def aggregate(self,emozione):
        for tipo in ('parola','emoji','emoticon','hashtag'):
            if tipo=='parola':
                campo_da_raggruppare='$lemma'
            else:
                campo_da_raggruppare='$token'
            stages = [
                {
                    '$match': {
                        'tipo': tipo,
                    }
                }, {
                    '$group': {
                        '_id': campo_da_raggruppare,
                        'quantita': {
                            '$sum': 1
                        },
                        'tipo': {
                            '$first': '$tipo'
                        }
                    }
                }, {
                    '$set': {
                        'token': '$_id'
                    }
                }, {
                    '$merge': {
                        'into': {
                            'db': 'tokens_aggregati',
                            'coll': emozione
                        },
                        'on': '_id',
                        'whenMatched': 'replace',
                        'whenNotMatched': 'insert'
                    }
                }
            ]
            conn=self._connect("token_twitter",emozione)
            res=conn.aggregate(stages)
            print(list(res))
            self._disconnect(conn)

if __name__ == '__main__':
    # pass
    mongodb_dao = MongoDBDAO("mongodb+srv://admin:admin@cluster0.9ajjj.mongodb.net/")
    # mongodb_dao.populate_db_twitter()
    # mongodb_dao.populate_db_lexres()
    mongodb_dao._test_download_messaggi()
    mongodb_dao._test_download_tutti_messaggi()