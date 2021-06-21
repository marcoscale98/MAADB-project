import os
from pprint import pprint

import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from impostazioni import *

emotions = ('anger', 'anticipation', 'disgust', 'fear', 'joy', 'sadness', 'surprise', 'trust')


def populate_db_lexres():
    # inseriamo nel database `buffer_lexical_resources` una collezione per ogni emozione
    #   per ogni parola
    #       inserisco la parola in un documento `lemma:<parola stessa`
    #       inserisco il nome della risorse e quante volte compare la parola stessa (1)
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


def upload_words(words: [str], emotion: str, type: str = 'word'):
    client = MongoClient()
    lex_res_db: Database = client['twitter_words']
    emot_coll: Collection = lex_res_db[emotion]
    if type not in ("word", 'hashtag', 'emoji', 'emoticon'):
        raise Exception('type not in ("word","hashtag","emoji","emoticon")')

    words = list(map(lambda word: add_type(word,type), words))
    result = emot_coll[emotion].insert_many(words)
    if DEBUG:
        print(f'Inseriti {len(result.inserted_ids)} {type} in {lex_res_db.name}.{emot_coll.name}')


def add_type(word, tipo):
    if type(word)==str:
        word= {
            'word':word,
            'type':tipo,
        }
    else:
        word['type'] = tipo
    return word


def upload_emoji(emoji, emotion):
    upload_words(emoji, emotion, "emoji")


def upload_emoticons(emoticons, emotion):
    upload_words(emoticons, emotion, "emoticon")


def upload_hashtags(hashtags, emotion):
    upload_words(hashtags, emotion, 'hashtag')


def populate_db_twitter():
    # inseriamo nella `backup_twitter_messages` database una collezione per ogni file txt
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


if __name__ == '__main__':
    client = MongoClient()
    twitter_db: Database = client['buffer_twitter_messages']
    lex_res_db: Database = client['buffer_lexical_resources']

    # populate_db_twitter()
    # populate_db_lexres()
