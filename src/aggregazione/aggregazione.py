'''
qui inserirò le funzioni per fare map-reduce sull'output del preprocessing
il risultato della map-reduce verrà inviato al MySQL DB

'''
from functools import reduce
from itertools import tee
from typing import Generator

from src.dao.mysql_dao import MySQLDAO
from src.utils import nomi_db_emozioni,config


def aggregate(tweets_prep:Generator):
    gen_hash,gen_emoji,gen_emot,gen_parole=tee(tweets_prep)
    hashtags=list(map(lambda tweet: tweet['hashtags'],gen_hash))
    emojis=list(map(lambda tweet: tweet['emojis'],gen_emoji))
    emoticons=list(map(lambda tweet: tweet['emoticons'],gen_emot))
    parole=list(map(lambda parola: parola['token'] ,map(lambda tweet: tweet['parole'],gen_parole)))
    return hashtags,emoticons,emojis,parole

# test: preprocesso pochi dati e provo ad aggregarli

def test_agggregate():
    dao=MySQLDAO(config.MYSQL_CONFIG)
    gen_mess=dao.download_messaggi_twitter('anger',10)


if __name__ == '__main__':
    test_agggregate()