import os
import timeit

from src.dao.mongodb_dao import MongoDBDAO
from src.dao.mysql_dao import MySQLDAO
from src.dao.nomi_db_emozioni import Emotions, Nomi_db
from src.preprocessing_text import *


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
        dao.upload_lemmi_of_lexres(em, lemmi,drop_if_not_empty)


def populate_db_twitter(dao, drop_if_not_empty):
    '''
    inseriamo nella `backup_twitter_messages` database una collezione per ogni file txt
    :return:
    '''
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
        print(f'Inseriti {res_insert} messaggi dell\'emozione {em}')


# def test():
#     client = MongoClient()
#     #emotion='anger'
#     Emotions = ('anger', 'anticipation', 'disgust', 'fear', 'joy', 'sadness', 'surprise', 'trust')
#     messages_db = client['buffer_twitter_messages']
#     words_db = client['twitter_words']
#     for emotion in Emotions:
#         print(timeit.Timer(lambda: test_one_emotion(emotion, messages_db, words_db)).timeit(number=1))
#
#
#
# def test_one_emotion(emotion, messages_db, words_db):
#     messages_coll = messages_db[emotion]
#     drop_words_collection(emotion, words_db)
#     frasi = messages_coll.find({})
#     mongodb_dao
#     for frase in frasi:
#         words, hashtags, emojis, emoticons = preprocessing_text(frase['message'])
#         if len(words) > 0:
#             upload_words(words, emotion)
#         if len(hashtags) > 0:
#             upload_words(hashtags, emotion, "hashtag")
#         if len(emojis) > 0:
#             upload_words(emojis, emotion, "emoji")
#         if len(emoticons) > 0:
#             upload_words(emoticons, emotion, "emoticon")
#
#
if __name__ == '__main__':
    DROP = True
    # dao = MongoDBDAO('mongodb+srv://admin:admin@cluster0.9ajjj.mongodb.net/')
    dao = MySQLDAO('jdbc:mysql://localhost:3306?serverTimezone=UTC')
    # populate_db_lexres(dao,DROP)
    populate_db_twitter(dao, DROP)
