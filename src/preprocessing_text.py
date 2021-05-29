import pprint
import re
from typing import Union, Iterator, Generator, List, Tuple, Dict

import nltk
from emojis import emojis
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from pymongo import MongoClient
from regex import regex

from res.Risorse_lessicali.Slang_words.slang_words import slang_words
from res.Risorse_lessicali.emoji_emoticons.emoji_emoticons import posemoticons, negemoticons


def search_emoticons(frase: str, emoticons: List = None) -> Tuple[str,List]:
    trovate = []
    if emoticons is None:
        (frase, trovate) = search_emoticons(frase,emoticons=posemoticons)
        frase, ems2 = search_emoticons(frase,emoticons=negemoticons)
        trovate.extend(ems2)
    else:
        while(len(emoticons)>0):
            em=emoticons.pop()
            index = frase.find(em)
            if index!=-1:
                trovate.append(em)
                frase = frase.replace(em,"",1)
                emoticons.append(em)
    return frase, trovate

def preprocessing_text(frase: str):
    '''
    Serie di operazioni svolte:
    - Eliminare USERNAME e URL
    - processare gli hashtag: possiamo contarli e fare statistiche anche su quelli o possiamo buttarli
    - processare emoji ed emoticons: contarli per fare statistiche e trovare sovrapposizioni di uso tra diverse emozioni
    - word tokenization: trovare le parole con _nltk.tokenize.word_tokenize_
    - riconoscere le forme di slang e sostituirle con le forme lunghe
    - trovare la punteggiatura e sostituirla con spazi bianchi
    - trasformare tutto a lower case
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
    frase, emoticons = search_emoticons(frase)
    tokens=word_tokenize(frase)
    print(tokens)
    #trovare le forme di slang e sostituirle con le forme estese
    #per ogni token
    #   cerco se è uno slang
    #       se lo è lo sostituisco con la forma estesa tokenizzata
    nuovi_tokens=[]
    for t in tokens:
        forma_estesa=slang_words.get(t)
        if forma_estesa is not None:
            nuovi_tokens.extend(word_tokenize(forma_estesa))
        else:
            nuovi_tokens.append(t)
    #pos tagging
    pos_tagged = nltk.pos_tag(nuovi_tokens)
    #remove stop words
    without_stop_words = [t for t in pos_tagged if t[0] not in stopwords.words('english')]
    #remove punteggiatura
    punt = ",.-;:_'?^!\"()[]{}<>£$%&=/*+"
    senza_punteggiatura = [t for t in without_stop_words if t[0] not in punt]
    #lemmatizer
    lemmatizer = WordNetLemmatizer()
    lemmatizzato = [lemmatizer.lemmatize(t[0],pos=t[1]) for t in senza_punteggiatura] #todo non funziona

    #tutto lower

    return frase, hashtags, list_ems, emoticons


def upload_words(words: [str], emotion: str):
    pass


if __name__ == '__main__':
    # client = MongoClient()
    # db = client['buffer_twitter_messages']
    # coll = db['anger']
    # frasi = coll.find({}).limit(30)
    frasi=[{'name':'hi clara, cu in the next days!'}]
    for frase in frasi:
        print('------------prima---------------')
        pprint.pprint(frase['name'])
        print('--------------dopo-------------')
        frase,hashtags,emoji,emoticons = preprocessing_text(frase['name'])
        pprint.pprint(frase,indent=2)
        pprint.pprint(hashtags,indent=2)
        pprint.pprint(emoji,indent=2)
        pprint.pprint(emoticons,indent=2)
