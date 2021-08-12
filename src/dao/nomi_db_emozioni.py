from enum import Enum


class Nomi_db_mongo(Enum):
    TWITTER_WORDS="twitter_words"
    LEX_RES_DB="lex_res_db"
    BUFFER_TWITTER_MESSAGES="buffer_twitter_messages"
    BUFFER_LEXICAL_RESOURCES= "buffer_lexical_resources"

class Nomi_db_mysql(Enum):
    EMOJI_CONTENUTA='emoji_contenuta'
    EMOTICON_CONTENUTA='emoticon_contenuta'
    HASHTAG_CONTENUTO = 'hashtag_contenuto'
    MESSAGGIO_TWITTER = 'messaggio_twitter'
    PAROLA='parola'
    PAROLA_CONTENUTA='parola_contenuta'
    RISORSA_LESSICALE='risorsa_lessicale'

class Emotions(Enum):
    ANGER='anger'
    ANTICIPATION='anticipation'
    DISGUST='disgust'
    FEAR='fear'
    JOY='joy'
    SADNESS='sadness'
    SURPRISE='surprise'
    TRUST='trust'

class Risorse(Enum):
    EmoSN='EmoSN'
    NRC='NRC'
    sentisense='sentisense'