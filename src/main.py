import json
import os
from itertools import chain, tee

from src.aggregazione.mongodb.aggregazione import aggregazione
from src.aggregazione.mysql.aggregazione import aggregate
from src.dao.mongodb_dao import MongoDBDAO
from src.dao.mysql_dao import MySQLDAO
from src.dao.dao import DAO
from src.utils import config
from src.utils.nomi_db_emozioni import Emotions, Nomi_db_mongo
from src.preprocessing_text import preprocessing_text


def populate_db_lexres(dao,drop_if_not_empty):
    # inseriamo nel database `buffer_lexical_resources` una collezione per ogni emozione
    #   per ogni parola
    #       inserisco la parola in un documento `lemma:<parola stessa>`
    #       inserisco il nome della risorse e quante volte compare la parola stessa (1)
    for em in Emotions:
        em = em.value
        lemmi = {}
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
        res_insert=dao.upload_lemmi_of_lexres(em, lemmi,drop_if_not_empty)
        print(f'Inseriti {res_insert} lemmi dell\'emozione {em}')

def populate_db_twitter(dao, drop_if_not_empty:bool=False):
    '''
    inseriamo nella `backup_twitter_messages` database una collezione per ogni file txt
    :return:
    '''
    n=True
    for em in Emotions:
        em = em.value
        path = f'res/Twitter_messaggi/dataset_dt_{em}_60k.txt'
        messages = []
        path = os.path.relpath(path)
        # leggiamo tutti i messaggi di una emozione
        with open(path, 'r', encoding='utf-8') as fp:
            mess = fp.readline()
            while (mess):
                messages.append(mess)
                mess = fp.readline()
        res_insert = dao.upload_twitter_messages(em, messages, drop_if_not_empty)
        if n and isinstance(dao,MySQLDAO) :
            drop_if_not_empty=False
        print(f'Inseriti {res_insert} messaggi dell\'emozione {em}')

def test_get_messaggi(dao,emozione=None):
    if emozione is None:
        emozione='anger'
    gen=dao.download_messaggi_twitter(emozione)
    for mess in gen:
        print(mess)

def test_connessione(dao):
    res=dao.test_connessione()
    if res:
        print("Connessione avvenuta con successo")

def _map(tweets_prep):
    tweets_prep=tweets_prep.values()
    gen_hash, gen_emoji, gen_emot, gen_parole = tee(tweets_prep, 4)
    hashtags = list(map(lambda tweet: tweet['hashtags'], gen_hash))
    hashtags = chain.from_iterable(hashtags)
    emojis = list(map(lambda tweet: tweet['emojis'], gen_emoji))
    emojis = chain.from_iterable(emojis)
    emoticons = list(map(lambda tweet: tweet['emoticons'], gen_emot))
    emoticons = chain.from_iterable(emoticons)
    parole = map(lambda tweet: tweet['parole'], gen_parole)
    parole_list_flat = chain.from_iterable(list(parole))
    return list(hashtags), list(emoticons), list(emojis), list(parole_list_flat)

def insert_tokens(dao:DAO,emozione, limit=None,use_backup=False):
    if use_backup:
        tweets_preprocessati=load_preprocessed('tweet_preprocessed')
    else:
        print('scarico tweets')
        messaggi=dao.download_messaggi_twitter(emozione=emozione,limit=limit)
        print('preprocesso tweets')
        tweet_preprocessati=preprocessing_text.preprocessing_text((t['message'] for t in messaggi))
        save_preprocessing(tweet_preprocessati,'tweet_preprocessed')
        if type(dao)==MySQLDAO:
            print('aggrego tweets')
            hashtags,emoticons,emojis,parole=aggregate(tweet_preprocessati)
        elif type(dao)==MongoDBDAO:
            dao._drop_if_not_empty(Nomi_db_mongo.TOKEN_TWITTER.value, 'anger')
            print('Inizio map')
            hashtags,emoticons,emojis,parole=_map(tweet_preprocessati)

        n = dao.upload_emoji(emojis, emozione)
        print(f'{n} emojis inserite')

        n = dao.upload_hashtags(hashtags, emozione)
        print(f'{n} hashtags inseriti')

        n = dao.upload_emoticons(emoticons, emozione)
        print(f'{n} emoticons inserite')

        n = dao.upload_words(parole, emozione)
        print(f'{n} parole inserite')


def test_insert_parola(dao):
    res=dao.upload_words(["parola"],"anger")
    print(f"Inserito {res} parole")

def test_insert_hashtag(dao):
    res=dao.upload_hashtags(["#hashtag"],'anger')
    print(f"Inserito {res} hashtags")

def test_insert_emoji(dao):
    res=dao.upload_emoji(['😀'],'anger')
    print(f'Inseriti {res} emoji')

def test_insert_emoticon(dao):
    res=dao.upload_emoticons([':)'],'anger')
    print(f'Inseriti {res} emoticon')

def test_aggregate_mongo(mongo_dao:MongoDBDAO,drop_if_not_empty=False):
    aggregazione(mongo_dao,'anger',drop_if_not_empty)

def save_preprocessing(lista,tipo):
    cartella='src/preprocessing_text/json/'
    file=cartella+tipo+'.json'
    mode='w'
    if not os.path.exists(file):
        mode='x'
    with open(file,mode) as fp:
        json.dump(lista,fp)

def load_preprocessed(tipo):
    cartella = 'src/preprocessing_text/json/'
    file = cartella + tipo + '.json'
    mode = 'r'
    with open(file,mode) as fp:
        objs=json.load(fp)
    return objs

if __name__ == '__main__':
    DROP = True
    USE_BACKUP=False
    dao = MongoDBDAO(config.MONGO_CONFIG)
    # dao = MySQLDAO(MYSQL_CONFIG)
    # test_connessione(dao)
    # populate_db_lexres(dao,DROP)
    # populate_db_twitter(dao, DROP)
    # dao._test_download_messaggi()
    # test_insert_parola(dao)
    # test_insert_emoticon(dao)
    # test_insert_emoji(dao)
    # test_insert_hashtag(dao)

    # insert_tokens(dao,'anger',use_backup=USE_BACKUP)
    test_aggregate_mongo(dao,DROP)