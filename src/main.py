import timeit

from src.preprocessing_text import *


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
# if __name__ == '__main__':
#
#     test_one_emotion()

