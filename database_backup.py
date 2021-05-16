import os
from pprint import pprint

import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

if __name__ == '__main__':
    client=MongoClient()
    twitter_db:Database=client['backup_twitter_messages']
    lex_res_db:Database = client['backup_lexical_resources']

    #inseriamo nella `backup_twitter_messages` database una collezione per ogni file txt
    emotions = ('anger','anticipation','disgust','fear','joy','sadness','surprise','trust')
    for em in emotions:
        emot_coll:Collection=twitter_db[em]
        if emot_coll.count_documents({})>0:
            emot_coll.drop()
        path=f'res/Twitter_messaggi/dataset_dt_{em}_60k.txt'
        messages=[]
        path=os.path.relpath(path)
        #leggiamo tutti i messaggi di una emozione
        with open(path,'r',encoding='utf-8') as fp:
            mess=fp.readline()
            while(mess):
                messages.append(mess)
                mess=fp.readline()
        messages = list(map(lambda m: {"name":m},messages))
        res_insert = emot_coll.insert_many(messages)
        print(f'N. documenti inseriti nella collezione {emot_coll.name}: {len(res_insert.inserted_ids)}')
        print(f'n. documenti presenti nella collezione {emot_coll.name}: {emot_coll.count_documents({})}')
