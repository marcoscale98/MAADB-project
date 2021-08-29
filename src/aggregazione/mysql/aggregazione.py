'''
qui inserirò le funzioni per fare map-reduce sull'output del preprocessing
il risultato della map-reduce verrà inviato al MySQL DB

'''
import itertools
from itertools import groupby
from functools import reduce
from itertools import tee
from pprint import pprint
from typing import Generator, Iterator
from itertools import chain

from src.dao.mysql_dao import MySQLDAO
from src.preprocessing_text.preprocessing_text import Preprocessing
from src.utils import nomi_db_emozioni,config


def _reduce(lista):
    lista=sorted(lista)
    it= groupby(lista)
    diz=dict()
    for k,v in it:
        length=sum(1 for el in v)
        print(f'chiave: {k}')
        print(f'valore: {length}')
        diz[k]=length
    return diz


def aggregazione(tweets_prep:Iterator):
    '''
    restituisce una quadrupla di dizionari del tipo <parola,quantità>
    la quadrupla: hashtags,emoticons,emojis,parole
    '''
    hashtags,emoticons,emojis,parole= _map(tweets_prep.values())
    hashtags = _reduce(hashtags)
    emoticons = _reduce(emoticons)
    emojis = _reduce(emojis)
    parole = _reduce(parole)
    return hashtags,emoticons,emojis,parole

def _map(tweets_prep):
    gen_hash, gen_emoji, gen_emot, gen_parole = tee(tweets_prep, 4)
    hashtags = list(map(lambda tweet: tweet['hashtags'], gen_hash))
    hashtags = chain.from_iterable(hashtags)
    emojis = list(map(lambda tweet: tweet['emojis'], gen_emoji))
    emojis = chain.from_iterable(emojis)
    emoticons = list(map(lambda tweet: tweet['emoticons'], gen_emot))
    emoticons = chain.from_iterable(emoticons)
    parole = map(lambda tweet: tweet['parole'], gen_parole)
    parole_list_flat = chain.from_iterable(list(parole))
    parole = list(map(lambda tweet: tweet['lemma'], parole_list_flat))
    return list(hashtags), list(emoticons), list(emojis), parole


# test: preprocesso pochi dati e provo ad aggregarli

def test_agggregate():
    dao=MySQLDAO(config.MYSQL_CONFIG)
    gen_mess=dao.download_messaggi_twitter('anger',10)
    gen_mess=(tweet['message'] for tweet in gen_mess)
    prep=Preprocessing()
    tweets_prep=prep(gen_mess)
    hashtags,emoticons,emojis,parole=aggregazione(tweets_prep.values())
    print('HASHTAGS')
    pprint(hashtags, indent=2)
    print('EMOJIS')
    pprint(emojis ,indent=2)
    print('EMOTICONS')
    pprint(emoticons, indent=2)
    print('PAROLE')
    pprint(parole, indent=2)


if __name__ == '__main__':
    test_agggregate()