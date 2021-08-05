import os
from typing import Union

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from impostazioni import *
from src.dao.dao import DAO

emotions = ('anger', 'anticipation', 'disgust', 'fear', 'joy', 'sadness', 'surprise', 'trust')

class MongoDBDAO(DAO):

    def __init__(self, url):
        self.url=url

    def _connect(self, db):
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


    def populate_db_lexres(self):
        # inseriamo nel database `buffer_lexical_resources` una collezione per ogni emozione
        #   per ogni parola
        #       inserisco la parola in un documento `lemma:<parola stessa`
        #       inserisco il nome della risorse e quante volte compare la parola stessa (1)
        lex_res_db = self._connect("lex_res_db")
        for em in emotions:
            lemmi = {}
            emot_coll: Collection = lex_res_db[em]
            if emot_coll.count_documents({}) > 0:
                emot_coll.drop()
            start_path = f'res/Risorse_lessicali/Archive_risorse_lessicali/{str.capitalize(em)}/'
            end_path = f'_{em}.txt'
            name_lex_res = ('EmoSN', 'NRC', 'sentisense')
            # trova i lemmi nelle lexical resources
            for res in name_lex_res:
                try:
                    path = os.path.relpath(start_path + res + end_path)

                    # leggiamo tutti i lemmi presenti nella risorsa lessicale
                    with open(path, 'r', encoding='utf-8') as fp:
                        lemma = fp.readline()
                        while (lemma):
                            # rimuovo endline
                            lemma = lemma.replace("\n", "")
                            # rimuovo parole composte
                            if '_' not in lemma:
                                l = lemmi.get(lemma, {})
                                l[res] = 1
                                lemmi[lemma] = l
                            lemma = fp.readline()
                except FileNotFoundError:
                    pass
            lemmi = list(map(lambda kv: {"lemma": kv[0], "res": kv[1]}, lemmi.items()))
            res_insert = emot_coll.insert_many(lemmi)
            print(f'N. documenti inseriti nella collezione {emot_coll.name}: {len(res_insert.inserted_ids)}')
            print(f'n. documenti presenti nella collezione {emot_coll.name}: {emot_coll.count_documents({})}')

        self._disconnect(lex_res_db)

    def upload_words(self,words: list[Union[str,dict]], emotion: str, _type: str = 'word'):
        twitter_words_db = self._connect("twitter_words")
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

    def populate_db_twitter(self):
        # inseriamo nella `backup_twitter_messages` database una collezione per ogni file txt
        twitter_db=self._connect("backup_twitter_messages")
        for em in emotions:
            emot_coll: Collection = twitter_db[em]
            if emot_coll.count_documents({}) > 0:
                emot_coll.drop()
            path = f'res/Twitter_messaggi/dataset_dt_{em}_60k.txt'
            messages = []
            path = os.path.relpath(path)
            # leggiamo tutti i messaggi di una emozione
            with open(path, 'r', encoding='utf-8') as fp:
                mess = fp.readline()
                while (mess):
                    messages.append(mess)
                    mess = fp.readline()
            messages = list(map(lambda m: {"message": m}, messages))
            res_insert = emot_coll.insert_many(messages)
            print(f'N. documenti inseriti nella collezione {emot_coll.name}: {len(res_insert.inserted_ids)}')
            print(f'n. documenti presenti nella collezione {emot_coll.name}: {emot_coll.count_documents({})}')
        self._disconnect(twitter_db)

    def drop_words_collection(self,emotion):
        words_db = self._connect("twitter_words")
        words_coll = words_db[emotion]
        words_coll.drop()
        self._disconnect(words_db)


if __name__ == '__main__':
    pass
    # mongodb_dao = MongoDBDAO()
    # mongodb_dao.populate_db_twitter()
    # mongodb_dao.populate_db_lexres()