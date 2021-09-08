from enum import Enum


class Nomi_db_mongo(Enum):
    TOKEN_TWITTER= "token_twitter"
    RISORSA_LESSICALE= "risorsa_lessicale"
    MESSAGGIO_TWITTER= "messaggio_twitter"
    TOKENS_AGGREGATI="tokens_aggregati"

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
    nuova_risorsa='nuova_risorsa'