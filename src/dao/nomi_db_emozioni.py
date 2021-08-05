from enum import Enum


class nomi_db(Enum):
    TWITTER_WORDS:"twitter_words"

    BUFFER_TWITTER_MESSAGES:"buffer_twitter_messages"

    BUFFER_LEXICAL_RESOURCES: "buffer_lexical_resources"

class emotions(Enum):
    ANGER:'anger'
    ANTICIPATION:'anticipation'
    DISGUST:'disgust'
    FEAR:'fear'
    JOY:'joy'
    SADNESS:'sadness'
    SURPRISE:'surprise'
    TRUST:'trust'