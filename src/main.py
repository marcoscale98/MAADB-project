import os

from src.dao.mongodb_dao import MongoDBDAO
from src.dao.mysql_dao import MySQLDAO
from src.utils.nomi_db_emozioni import Emotions


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

if __name__ == '__main__':
    DROP = True
    # dao = MongoDBDAO('mongodb+srv://admin:admin@cluster0.9ajjj.mongodb.net/')
    dao = MySQLDAO('jdbc:mysql://localhost:3306?serverTimezone=UTC')
    populate_db_lexres(dao,DROP)
    # populate_db_twitter(dao, DROP)
    # test_get_messaggi(dao)
    # test_connessione(dao)