import pprint
import re
from typing import Union, Generator, List, Tuple

import spacy
from emojis import emojis as lib_emojis
from nltk.corpus import stopwords
from pymongo import MongoClient
from impostazioni import *


from res.Risorse_lessicali.Slang_words.slang_words import slang_words
from res.Risorse_lessicali.emoji_emoticons.emoji_emoticons import posemoticons, negemoticons

nlp = spacy.load('en_core_web_sm', disable=['ner'])
nlp.disable_pipe("parser")
nlp.enable_pipe("senter")

def search_emoticons(frase: str) -> Tuple[str, List]:
    trovate = []
    emoticons = posemoticons.union(negemoticons)
    while (len(emoticons) > 0):
        em = emoticons.pop()
        index = frase.find(em)
        if index != -1:
            trovate.append(em)
            frase = frase.replace(em, "", 1)
            emoticons.add(em)
    return frase, trovate

def preprocessing_text(frasi: Generator) -> dict[int, dict[str, Union[int, str, list, list]]]:
    '''
    Serie di operazioni svolte:
    - [x] Eliminare USERNAME e URL
    - [x] processare gli hashtag: possiamo contarli e fare statistiche anche su quelli o possiamo buttarli
    - [x] processare emoji ed emoticons: contarli per fare statistiche e trovare sovrapposizioni di uso tra diverse emozioni
    - [x] tokenization, lemmatization and pos tagging con *spacy*
    - [x] riconoscere le forme di slang e sostituirle con le forme lunghe
    - [x] eliminare stop words
    - [x] rimuovere la punteggiatura
    - [x] trasformare tutto a lower case

    :param frase:
    :return: preprocessed_text (es. {'token':'dog','lemma':'dog','pos':'NOUN'}), lista hashtag trovati, lista emoji trovate, lista emoticons trovate
    '''
    tweets_analizzati= dict()
    i=0
    for frase in frasi:
        emoticons, frase, hashtags, list_emojis = primo_processing(frase)
        tweets_analizzati[i]={"id":i, "frase_ripulita": frase,"hashtags":hashtags,"emoticons":emoticons,"emojis":list_emojis}
        i+=1

    frasi_tokenizzate:Generator = spacy_processing((tweet["frase_ripulita"] for tweet in tweets_analizzati.values())) # parte più costosa
    i=0
    for list_token in frasi_tokenizzate:
        parole_senza_punteggiatura = secondo_processing(list_token)
        tweets_analizzati[i]["parole"] = parole_senza_punteggiatura
        i+=1
    return tweets_analizzati

def secondo_processing(list_token):
    nuovi_tokens = slang_words_processing(list_token)
    # remove stop words
    without_stop_words = [t for t in nuovi_tokens if t['token'] not in stopwords.words('english')]
    # remuove punteggiatura, parole mal formate e eventuali caratteri speciali
    parole_senza_punteggiatura = [t for t in without_stop_words if t['pos'] not in {'SPACE', 'SYM', 'PUNCT', 'X'}]
    # tutto lower
    for t in parole_senza_punteggiatura:
        t['lemma'] = t['lemma'].lower()
    return parole_senza_punteggiatura

def primo_processing(frase):
    frase = replace_username_url(frase)
    frase, hashtags = extract_hashtags(frase)
    frase, list_ems = extract_emoji(frase)
    frase, emoticons = search_emoticons(frase)
    return emoticons, frase, hashtags, list_ems

def slang_words_processing(tokens):
    # trovare le forme di slang e sostituirle con le forme estese
    # per ogni token
    #   cerco se è uno slang
    #       se lo è lo sostituisco con la forma estesa tokenizzata
    nuovi_tokens = []
    for t in tokens:
        forma_estesa = slang_words.get(t['token'])
        if forma_estesa is not None:
            doc = nlp(forma_estesa)
            for token in doc:
                # print(f'{token.text} con lemma {token.lemma_} con pos: {token.pos_}')
                nuovi_tokens.append({'token': token.text, 'lemma': token.lemma_, 'pos': token.pos_})
        else:
            nuovi_tokens.append(t)
    return nuovi_tokens

def spacy_processing(frasi: Generator) -> Generator:
    # tokenization, lemmatization and pos tagging
    docs = nlp.pipe(frasi,n_process=8)

    def extract_token(doc):
        tokens = []
        for token in doc:
            tokens.append({'token': token.text, 'lemma': token.lemma_, 'pos': token.pos_})
        return tokens
    frasi_processate = (extract_token(doc) for doc in docs)
    return frasi_processate

def extract_emoji(frase):
    '''

    :param frase: frase dove trovare le emoji
    :return:
    '''
    list_ems = []
    ems: Generator = lib_emojis.iter(frase)  # in questo modo conta prende anche le ripetizioni
    for emoji in ems:
        frase = frase.replace(emoji, "")
        list_ems.append(emoji)
    return frase, list_ems

def extract_hashtags(frase):
    hashtags = re.findall(r'\B#\w*[a-zA-Z]+\w*', frase)
    for h in hashtags:
        frase = frase.replace(h, "", 1)
    return frase, hashtags

def replace_username_url(frase):
    frase = frase.replace("USERNAME", "").replace("URL", "")
    return frase

if __name__ == '__main__':
    print(nlp.pipe_names)

    client = MongoClient()
    db = client['buffer_twitter_messages']
    coll = db['anger']
    db_tokens = client['twitter_words'].drop_collection("anger")
    frasi = coll.find({}).limit(60000)
    frasi: Generator = (frase['message'] for frase in frasi)
    # frasi = [{'message': 'Pen is on the table!'}]
    tweet_analizzati = preprocessing_text(frasi)
    print("Finito preprocessing")
    lista = tweet_analizzati.values()
    hashtags = [ogg for sotto_lista in lista for ogg in sotto_lista['hashtags']]
    upload_hashtags(hashtags, 'anger')
    print(f'Caricati hashtags')
    emojis = [ogg for sotto_lista in lista for ogg in sotto_lista['emojis']]
    upload_emoji(emojis, 'anger')
    print(f'Caricati emojis')
    tokens = [ogg for sotto_lista in lista for ogg in sotto_lista['parole']]
    upload_words(tokens, 'anger')
    print(f'Caricati tokens')
    emoticons = [ogg for sotto_lista in lista for ogg in sotto_lista['emoticons']]
    upload_emoticons(emoticons, 'anger')
    print(f'Caricati emoticons')
    if DEBUG:
        pprint.pprint(hashtags)
        pprint.pp(emoticons)
        pprint.pp(emojis)
        pprint.pp(tokens)
