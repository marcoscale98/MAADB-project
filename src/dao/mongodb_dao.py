from pprint import pprint
from typing import Union, Optional, Generator

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.results import InsertManyResult

from src.dao.dao import DAO
from src.utils.config import MONGO_CONFIG

from src.utils.nomi_db_emozioni import Nomi_db_mongo, Risorse


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
            emozione_coll = self._connect(Nomi_db_mongo.MESSAGGIO_TWITTER.value,emozione)
            cursor=emozione_coll.find()[min:max]
            messaggi = list(cursor)
            self._disconnect(emozione_coll)
            min += 100
            max += 100
            if len(messaggi)==0:
                print("Messaggi finiti")
                return
            for mess in messaggi:
                yield mess

    def download_parole_risorse_lessicali(self, emozione, risorsa=None)-> list:
        collezione:Collection=self._connect(Nomi_db_mongo.RISORSA_LESSICALE.value,emozione)
        if risorsa:
            docs = collezione.find({f'risorse.{risorsa}':1})
        else:
            docs=collezione.find({})
        docs=list(doc['lemma'] for doc in docs)
        self._disconnect(collezione)
        return docs


    def upload_nuove_parole_tweets(self, parole, emozione):
        coll = self._connect(Nomi_db_mongo.RISORSA_LESSICALE.value, emozione)
        inserted = coll.insert_many([{'lemma': parola, 'risorse': {Risorse.nuova_risorsa.value:1}} for parola in parole])
        self._disconnect(coll)
        return len(inserted.inserted_ids)

    def test_connessione(self):
        conn=self._connect("test","test")
        self._disconnect(conn)
        print("Connessione avvenuta con successo")

    def download_emojis(self,emozione,limit=0) -> dict:
        '''

        :param emozione:
        :param limit:
        :return:
        '''
        coll=self._connect(Nomi_db_mongo.TOKENS_AGGREGATI.value,emozione)
        cursor=coll.find(
            {'tipo':'emoji'}, #filter
            {'_id':0}, #project
            limit=limit,
        )
        res={}
        cursor.batch_size(100)
        for obj in cursor:
            res[obj['token']]=obj['quantita']
        self._disconnect(coll)
        return res

    def download_emoticons(self,emozione,limit=0) -> dict:
        '''

        :param emozione:
        :param limit:
        :return:
        '''
        coll = self._connect(Nomi_db_mongo.TOKENS_AGGREGATI.value, emozione)
        cursor = coll.find(
            {'tipo': 'emoticon'},  # filter
            {'_id': 0},  # project
            limit=limit,
        )
        res = {}
        cursor.batch_size(100)
        for obj in cursor:
            res[obj['token']] = obj['quantita']
        self._disconnect(coll)
        return res

    def download_parole_tweets(self, emozione, limit=0) -> dict:
        '''

        :param emozione:
        :param limit:
        :return:
        '''
        coll = self._connect(Nomi_db_mongo.TOKENS_AGGREGATI.value, emozione)
        cursor = coll.find(
            {'tipo': 'parola'},  # filter
            {'_id': 0},  # project
            limit=limit,
        )
        res = {}
        cursor.batch_size(100)
        for obj in cursor:
            res[obj['token']] = obj['quantita']
        self._disconnect(coll)
        return res

    def clear_databases(self):
        for db_name in Nomi_db_mongo:
            db:Database=self._connect(db_name.value)
            filter = {"name": {"$regex": r"^(?!system\.)"}}
            collezioni=db.list_collection_names(filter=filter)
            for coll in collezioni:
                db.drop_collection(coll)
            self._disconnect(db)

    def _test_insert_parola(dao):
        super()._test_insert_parola()

    def _test_insert_hashtag(dao):
        super()._test_insert_hashtag()

    def _test_insert_emoji(dao):
        super()._test_insert_emoji()

    def _test_insert_emoticon(dao):
        super()._test_insert_emoticon()

    def download_hashtags(self,emozione,limit=0) -> dict:
        '''

        :param emozione:
        :param limit:
        :return:
        '''
        coll = self._connect(Nomi_db_mongo.TOKENS_AGGREGATI.value, emozione)
        cursor = coll.find(
            {'tipo': 'hashtag'},  # filter
            {'_id': 0},  # project
            limit=limit,
        )
        res = {}
        cursor.batch_size(100)
        for obj in cursor:
            res[obj['token']] = obj['quantita']
        self._disconnect(coll)
        return res

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
            self._disconnect(conn)

    def _test_download_lemmi_lex_res(self):
        parole=self.download_parole_risorse_lessicali('anger','EmoSN')
        print(parole)

if __name__ == '__main__':
    # pass
    mongodb_dao = MongoDBDAO(MONGO_CONFIG)
    mongodb_dao.test_connessione()
    # mongodb_dao.populate_db_twitter()
    # mongodb_dao.populate_db_lexres()
    # mongodb_dao._test_download_messaggi()
    # mongodb_dao._test_download_tutti_messaggi()
    # emojis=mongodb_dao.download_emojis('anger',limit=10)
    # emoticons=mongodb_dao.download_emoticons('anger',limit=10)
    # parole=mongodb_dao.download_parole_tweets('anger', limit=10)
    # hashtags=mongodb_dao.download_hashtags('anger',limit=10)
    # pprint(emojis,indent=2)
    # pprint(emoticons,indent=2)
    # pprint(parole,indent=2)
    # pprint(hashtags,indent=2)
    # mongodb_dao._test_download_lemmi_lex_res()