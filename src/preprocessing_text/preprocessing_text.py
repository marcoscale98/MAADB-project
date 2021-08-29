import json
import os
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

class Preprocessing():

    def __init__(self) -> None:
        self.nlp = spacy.load('en_core_web_sm', disable=['ner'])
        self.nlp.disable_pipe("parser")
        self.nlp.enable_pipe("senter")

    def search_emoticons(self,frase: str) -> Tuple[str, List]:
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

    def preprocessing_text(self,frasi: Generator) -> dict[int, dict[str, Union[int, str, list, list]]]:
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
            emoticons, frase, hashtags, list_emojis = self.primo_processing(frase)
            tweets_analizzati[i]={"id":i, "frase_ripulita": frase,"hashtags":hashtags,"emoticons":emoticons,"emojis":list_emojis}
            i+=1

        frasi_tokenizzate:Generator = self.spacy_processing((tweet["frase_ripulita"] for tweet in tweets_analizzati.values())) # parte più costosa
        i=0
        for list_token in frasi_tokenizzate:
            parole_senza_punteggiatura = self.secondo_processing(list_token)
            tweets_analizzati[i]["parole"] = parole_senza_punteggiatura
            i+=1
        return tweets_analizzati

    def secondo_processing(self,list_token):
        nuovi_tokens = self.slang_words_processing(list_token)
        # remove stop words
        without_stop_words = [t for t in nuovi_tokens if t['token'] not in stopwords.words('english')]
        # remuove punteggiatura, parole mal formate e eventuali caratteri speciali
        parole_senza_punteggiatura=[]
        for t in without_stop_words:
            if t['pos'] not in ('SPACE', 'SYM', 'PUNCT', 'X'):
                if t['token'] not in "&?!^,.-;:_+*[]{}=()/|\\\"'<>`´´‹~¥‘“«":
                    parole_senza_punteggiatura.append(t)
        # tutto lower
        for t in parole_senza_punteggiatura:
            t['lemma'] = t['lemma'].lower()
        return parole_senza_punteggiatura

    def primo_processing(self,frase):
        frase = self.replace_username_url(frase)
        frase, hashtags = self.extract_hashtags(frase)
        frase, list_ems = self.extract_emoji(frase)
        frase, emoticons = self.search_emoticons(frase)
        return emoticons, frase, hashtags, list_ems

    def slang_words_processing(self,tokens):
        # trovare le forme di slang e sostituirle con le forme estese
        # per ogni token
        #   cerco se è uno slang
        #       se lo è lo sostituisco con la forma estesa tokenizzata
        nuovi_tokens = []
        for t in tokens:
            forma_estesa = slang_words.get(t['token'])
            if forma_estesa is not None:
                doc = self.nlp(forma_estesa)
                for token in doc:
                    # print(f'{token.text} con lemma {token.lemma_} con pos: {token.pos_}')
                    nuovi_tokens.append({'token': token.text, 'lemma': token.lemma_, 'pos': token.pos_})
            else:
                nuovi_tokens.append(t)
        return nuovi_tokens

    def spacy_processing(self,frasi: Generator) -> Generator:
        # tokenization, lemmatization and pos tagging
        docs = self.nlp.pipe(frasi,n_process=8)

        def extract_token(doc):
            tokens = []
            for token in doc:
                tokens.append({'token': token.text, 'lemma': token.lemma_, 'pos': token.pos_})
            return tokens
        frasi_processate = (extract_token(doc) for doc in docs)
        return frasi_processate

    def extract_emoji(self,frase):
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

    def extract_hashtags(self,frase):
        hashtags = re.findall(r'\B#\w*[a-zA-Z]+\w*', frase)
        for h in hashtags:
            frase = frase.replace(h, "", 1)
        return frase, hashtags

    def replace_username_url(self,frase):
        frase = frase.replace("USERNAME", "").replace("URL", "")
        return frase

    def save_preprocessing(self,lista, tipo):
        cartella = 'src/preprocessing_text/json/'
        file = cartella + tipo + '.json'
        mode = 'w'
        if not os.path.exists(file):
            mode = 'x'
        with open(file, mode) as fp:
            json.dump(lista, fp)

    def load_preprocessed(self,tipo):
        cartella = 'src/preprocessing_text/json/'
        file = cartella + tipo + '.json'
        mode = 'r'
        with open(file, mode) as fp:
            objs = json.load(fp)
        return objs

    def _test_preprocessing(self):
        def frasi():
            yield "I love you :)"
            yield "I hate you 😡"
            yield "My dog wants to eat #lunchtime"
        gen=frasi()
        res=self.preprocessing_text(gen)
        pprint.pprint(res,indent=2)
        return res

    def _test_save_and_load(self):
        res=self._test_preprocessing()
        self.save_preprocessing(res,'prova')
        dati_salvati=self.load_preprocessed('prova')
        pprint.pprint(dati_salvati)

if __name__ == '__main__':
    prep=Preprocessing()
    # prep._test_preprocessing()
    prep._test_save_and_load()
    # pass
