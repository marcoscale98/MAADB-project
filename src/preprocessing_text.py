import pprint
import re
from typing import Union, Iterator, Generator

from emojis import emojis
from nltk.tokenize import word_tokenize
from pymongo import MongoClient
from regex import regex


def preprocessing_text(frase: str):
    '''
    Serie di operazioni svolte:
    - Eliminare USERNAME e URL
    - processare gli hashtag: possiamo contarli e fare statistiche anche su quelli o possiamo buttarli
    - processare emoji ed emoticons: contarli per fare statistiche e trovare sovrapposizioni di uso tra diverse emozioni
    - riconoscere le forme di slang e sostituirle con le forme lunghe
    - trovare la punteggiatura e sostituirla con spazi bianchi
    - trasformare tutto a lower case
    - word tokenization: trovare le parole con _nltk.tokenize.word_tokenize_
    - POS tagging
    - eliminare stop words
    - lemming

    :param frase:
    :return: lista di parole utili, lista hashtag trovati, lista emoji trovate, lista emoticons trovate
    '''
    frase = frase.replace("USERNAME", "").replace("URL", "")
    hashtags = re.findall(r'\B#\w*[a-zA-Z]+\w*', frase)
    for h in hashtags:
        frase = frase.replace(h, "", 1)
    ems:Generator= emojis.iter(frase) #in questo modo conta prende anche le ripetizioni
    list_ems=[]
    for emoji in ems:
        frase = frase.replace(emoji, "")
        list_ems.append(emoji)
    return frase, hashtags, list_ems


def upload_words(words: [str], emotion: str):
    pass


if __name__ == '__main__':
    client = MongoClient()
    db = client['buffer_twitter_messages']
    coll = db['anger']
    frasi = coll.find({}).limit(15)
    for frase in frasi:
        print('------------prima---------------')
        pprint.pprint(frase['name'])
        print('--------------dopo-------------')
        frase,hashtags,emoji = preprocessing_text(frase['name'])
        pprint.pprint(frase,indent=2)
        pprint.pprint(hashtags,indent=2)
        pprint.pprint(emoji,indent=2)
