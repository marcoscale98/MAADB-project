import pprint
import re
from typing import Union, Iterator, Generator, List, Tuple, Dict

import nltk
import spacy
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
    - [x] Eliminare USERNAME e URL
    - [x] processare gli hashtag: possiamo contarli e fare statistiche anche su quelli o possiamo buttarli
    - [x] processare emoji ed emoticons: contarli per fare statistiche e trovare sovrapposizioni di uso tra diverse emozioni
    - [x] tokenization, lemmatization and pos tagging con *spacy*
    - [x] riconoscere le forme di slang e sostituirle con le forme lunghe
    - [x] POS tagging
    - [x] eliminare stop words
    - [x] rimuovere la punteggiatura
    - [x] trasformare tutto a lower case

    :param frase:
    :return: lista di parole utili, preprocessed_text (es. {'word':'dog','lemma':'dog','pos':'NOUN'}), lista hashtag trovati, lista emoji trovate, lista emoticons trovate
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

    nlp=spacy.load('en_core_web_sm')
    #tokenization, lemmatization and pos tagging
    doc=nlp(frase)
    tokens=[]
    for token in doc:
        print(f'{token.text} con lemma {token.lemma_} con pos: {token.pos_}')
        tokens.append({'word':token.text,'lemma':token.lemma_,'pos':token.pos_})
    #trovare le forme di slang e sostituirle con le forme estese
    #per ogni token
    #   cerco se è uno slang
    #       se lo è lo sostituisco con la forma estesa tokenizzata
    nuovi_tokens=[]
    for t in tokens:
        forma_estesa=slang_words.get(t['word'])
        if forma_estesa is not None:
            doc=nlp(forma_estesa)
            for token in doc:
                print(f'{token.text} con lemma {token.lemma_} con pos: {token.pos_}')
                nuovi_tokens.append({'word': token.text, 'lemma': token.lemma_, 'pos': token.pos_})
        else:
            nuovi_tokens.append(t)
    #remove stop words
    without_stop_words = [t for t in nuovi_tokens if t['word'] not in stopwords.words('english')]
    #remove punteggiatura
    punt = ",.-;:_'?^!\"()[]{}<>£$%&=/*+"
    senza_punteggiatura = [t for t in without_stop_words if t['word'] not in punt]
    #tutto lower
    for t in senza_punteggiatura:
        t['lemma']=t['lemma'].lower()

    return frase, senza_punteggiatura, hashtags, list_ems, emoticons


def upload_words(words: [str], emotion: str):
    pass

def upload_emoji(emoji,emotion):
    pass
def upload_emoticons(emoticons,emotion):
    pass
def upload_hashtags(hashtags,emotion):
    pass

if __name__ == '__main__':
    # client = MongoClient()
    # db = client['buffer_twitter_messages']
    # coll = db['anger']
    # frasi = coll.find({}).limit(30)
    frasi=[{'name':'Pen is on the table!'}]
    for frase in frasi:
        print('------------prima---------------')
        pprint.pprint(frase['name'])
        print('--------------dopo-------------')
        frase, preprocessed_text, hashtags,emoji,emoticons = preprocessing_text(frase['name'])
        pprint.pprint(f'frase:{frase}',indent=2)
        pprint.pprint(f'preprocessed_text: {preprocessed_text}',indent=2)
        pprint.pprint(f'hashtags: {hashtags}',indent=2)
        pprint.pprint(f'emoji: {emoji}',indent=2)
        pprint.pprint(f'emoticons: {emoticons}',indent=2)
