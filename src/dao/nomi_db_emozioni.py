from enum import Enum


class Nomi_db(Enum):
    TWITTER_WORDS="twitter_words"
    LEX_RES_DB="lex_res_db"
    BUFFER_TWITTER_MESSAGES="buffer_twitter_messages"
    BUFFER_LEXICAL_RESOURCES= "buffer_lexical_resources"

class Emotions(Enum):
    ANGER='anger'
    ANTICIPATION='anticipation'
    DISGUST='disgust'
    FEAR='fear'
    JOY='joy'
    SADNESS='sadness'
    SURPRISE='surprise'
    TRUST='trust'