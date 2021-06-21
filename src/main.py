from src.preprocessing_text import *
from src.database_buffer import *

client = MongoClient()
emotion='anger'
messages_db = client['buffer_twitter_messages']
messages_coll = messages_db[emotion]
words_db = client['twitter_words']
words_coll = words_db[emotion]
words_coll.drop()
frasi = messages_coll.find({}).limit(20)
for frase in frasi:
    words,hashtags,emojis,emoticons=preprocessing_text(frase['message'])
    if len(words)>0:
        upload_words(words,emotion)
    if len(hashtags)>0:
        upload_words(hashtags,emotion,"hashtag")
    if len(emojis)>0:
        upload_words(emojis,emotion,"emoji")
    if len(emoticons)>0:
        upload_words(emoticons,emotion,"emoticon")
