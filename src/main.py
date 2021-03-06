import itertools
import json
import os
import time
from itertools import chain, tee
from wordcloud import wordcloud, WordCloud
import matplotlib.pyplot as plt

from src.aggregazione.mongodb.aggregazione import aggregazione as aggregazione_mongo
from src.aggregazione.mysql.aggregazione import aggregazione as aggregazione_mysql

from src.dao.mongodb_dao import MongoDBDAO
from src.dao.mysql_dao import MySQLDAO
from src.dao.dao import DAO
from src.preprocessing_text.preprocessing_text import Preprocessing
from src.utils import config, nomi_db_emozioni
from src.utils.nomi_db_emozioni import Emotions, Nomi_db_mongo, Risorse
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
        # trova i lemmi nelle lexical resources
        for res in Risorse:
            if res==Risorse.nuova_risorsa:
                continue
            res=res.value
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
        lemmi = list(map(lambda kv: {"lemma": kv[0], "risorse": kv[1]}, lemmi.items()))
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

def insert_tokens(dao:DAO,emozione, limit=None,use_backup=False,drop=False):
    '''
    scarica i messaggi twitter, li preprocessa, li aggrega (nel caso di mysql) e poi fa upload
    :param dao:
    :param emozione:
    :param limit:
    :param use_backup:
    :param drop:
    :return:
    '''
    tweet_preprocessati = preprocessing_tweets(dao, emozione, limit, use_backup)

    if type(dao)==MySQLDAO:
        print('aggrego tweets')
        hashtags,emoticons,emojis,parole=aggregazione_mysql(tweet_preprocessati)
    elif type(dao)==MongoDBDAO:
        if drop:
            dao._drop_if_not_empty(Nomi_db_mongo.TOKEN_TWITTER.value, 'anger')
        print('Inizio mapping')
        hashtags,emoticons,emojis,parole=_map(tweet_preprocessati)

    n = dao.upload_emoji(emojis, emozione)
    print(f'{n} emojis inserite')

    n = dao.upload_hashtags(hashtags, emozione)
    print(f'{n} hashtags inseriti')

    n = dao.upload_emoticons(emoticons, emozione)
    print(f'{n} emoticons inserite')

    n = dao.upload_words(parole, emozione)
    print(f'{n} parole inserite')

def preprocessing_tweets(dao, emozione, limit, use_backup):
    prep = Preprocessing(emozione)
    if use_backup:
        tweet_preprocessati = prep.load_preprocessed()
    else:
        print('scarico tweets')
        messaggi = dao.download_messaggi_twitter(emozione=emozione, limit=limit)
        print('preprocesso tweets')
        tweet_preprocessati = prep.preprocessing_text((t['message'] for t in messaggi))
        prep.save_preprocessing(tweet_preprocessati)
    return tweet_preprocessati

def print_wordclouds(dao:DAO,tipo:str,emozione:str,save=False):
    '''
    disegna la word cloud dei token pi?? utilizzati nei tweets dell' *emozione* data
    :param tipo: 'emoji','emoticon','parola','hashtag'
    :param emozione:
    :return:
    '''

    if tipo=='emoji':
        d = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
        font_path = os.path.join(os.getcwd(),'res', 'font', 'Symbola.ttf')
        tokens=dao.download_emojis(emozione)
        wordcloud = WordCloud(max_words=15, font_path=font_path).generate_from_frequencies(tokens)
    elif tipo=='parola':
        tokens=dao.download_parole_tweets(emozione)
    elif tipo=='emoticon':
        tokens=dao.download_emoticons(emozione)
    elif tipo=='hashtag':
        tokens=dao.download_hashtags(emozione)
    else:
        raise Exception('Errore nel tipo')
    if tipo!='emoji':
        wordcloud=WordCloud(max_words=15).generate_from_frequencies(tokens)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.title(f'{str.capitalize(emozione)} : {str.capitalize(tipo)}')
    plt.axis("off")
    if save:
        path=os.path.join('res','immagini_output',f'{emozione}-{tipo}.jpg')
        plt.savefig(path,transparent=True)
    plt.show()

def calcolo_parole_shared(dao:DAO, emozione:str):
    '''
    - scarico le parole presenti nei tweets di una emozione
    - scarico le parole presenti nelle risorse lessicali in una emozione
    - trovo l'intersezione tra le 2
    :return:
    '''
    parole_tweets=dao.download_parole_tweets(emozione).keys()
    parole_tweets=set().union(parole_tweets)
    #print(f'{emozione}')
    percentuali=[]
    etichette=[]
    for res in Risorse:
        if res==Risorse.nuova_risorsa:
            continue
        res=res.value
        parole_res=dao.download_parole_risorse_lessicali(emozione,res)
        if len(parole_res)==0:
            continue
        parole_res=set().union(parole_res)
        intersezione=parole_tweets.intersection(parole_res)
        perc=len(intersezione)/len(parole_res)
        percentuali.append(perc)
        etichette.append(f'{emozione}-{res}')
        #print(f'Percentuale di parole_shared/parole_res per la risorsa {res}: {perc}')
    return etichette,percentuali

def trova_nuove_parole_nei_tweets(dao,emozione):
    '''
    si preoccupa di trovare l'intersezione tra parole nelle lexical resources e nei tweets
    :param dao:
    :return:
    '''
    parole_tweets = dao.download_parole_tweets(emozione).keys()
    parole_tweets = set().union(parole_tweets)
    parole_res = dao.download_parole_risorse_lessicali(emozione)
    parole_res = set().union(parole_res)
    nuove_parole = parole_tweets.difference(parole_res)
    return nuove_parole


def pipeline(dao:DAO,drop,use_backup,save_images):
    if drop:
        dao.clear_databases()
    populate_db_lexres(dao,drop)
    populate_db_twitter(dao,drop)
    for emozione in nomi_db_emozioni.Emotions:
        emozione=emozione.value
        print(f'\nEmozione: {emozione}')
        insert_tokens(dao,emozione,use_backup=use_backup,drop=drop)
        if type(dao)==MongoDBDAO:
            print('Aggregazione dei tokens')
            aggregazione_mongo(dao,emozione,drop)
        for tipo in ('emoji','parola','hashtag','emoticon'):
            print(f'Visualizzo word_cloud per {tipo}')
            print_wordclouds(dao,tipo,emozione,save_images)
    print("Visualizzo istogramma")
    display_istogramma(dao, save_images)
    print('\n')
    for emozione in nomi_db_emozioni.Emotions:
        emozione=emozione.value
        nuove_parole = trova_nuove_parole_nei_tweets(dao,emozione)
        upload_nuove_parole_tweets(dao, emozione, nuove_parole)

def display_wordclouds_istogramma(dao,save_images):
    for emozione in nomi_db_emozioni.Emotions:
        emozione=emozione.value
        print(f'\nEmozione: {emozione}')
        for tipo in ('emoji','parola','hashtag','emoticon'):
            print(f'Visualizzo word_cloud per {tipo}')
            print_wordclouds(dao,tipo,emozione,save_images)
    print("Visualizzo istogramma")
    display_istogramma(dao, save_images)

def upload_nuove_parole_tweets(dao, emozione, nuove_parole):
    n_inserted = dao.upload_nuove_parole_tweets(nuove_parole, emozione)
    print(f'Inserite {n_inserted} nuove parole per {emozione}')

def delete_database(dao):
    dao.clear_databases()

def display_istogramma(dao, save=False):
    '''
    crea un istogramma per visualizzare la percentuale di parole shared tra parole_tweets e parole_risorse, per ogni risorsa per ogni emozione
    :param dao:
    :return: plotta l'istogramma a barre
    '''
    etichette2,percentuali2=[],[]
    for em in Emotions:
        em=em.value
        etichette,percentuali=calcolo_parole_shared(dao, em)
        etichette2.extend(etichette)
        percentuali2.extend(percentuali)
    plt.barh(etichette2,percentuali2)
    plt.autoscale(True)
    if save:
        plt.savefig('res/immagini_output/istogramma.jpg',transparent=True)
    plt.show()


def test_print_wordclouds(dao):
    tipo='parola'
    emozione='trust'
    print_wordclouds(dao,tipo,emozione, save=True)

def test_upload_nuove_parole(dao):
    emozione='anger'
    nuove_parole = trova_nuove_parole_nei_tweets(dao, emozione)
    upload_nuove_parole_tweets(dao, emozione, nuove_parole)

if __name__ == '__main__':
    DROP = False
    USE_BACKUP=True
    SAVE_IMAGES=False
    # dao = MongoDBDAO(config.MONGO_CONFIG)
    dao = MySQLDAO(config.MYSQL_CONFIG)

    # dao.clear_databases()
    # dao.test_connessione()
    pipeline(dao,DROP,USE_BACKUP,SAVE_IMAGES)
    # display_wordclouds_istogramma(dao,SAVE_IMAGES)
    # test_print_wordclouds(dao)
    # test_upload_nuove_parole(dao)
    # make_histograms(dao)
    # delete_database(dao)
    # populate_db_lexres(dao,DROP)
    # populate_db_twitter(dao, DROP)
    # dao._test_download_messaggi()
    # test_insert_parola(dao)
    # test_insert_emoticon(dao)
    # test_insert_emoji(dao)
    # test_insert_hashtag(dao)

    # insert_tokens(dao,'anger',use_backup=USE_BACKUP)
    # test_aggregate_mongo(dao,DROP)
    # test_print_wordclouds(dao)