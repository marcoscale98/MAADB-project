from src.dao.mongodb_dao import *

def aggregazione(dao:MongoDBDAO,emozione, drop_if_not_empty=None):
    if drop_if_not_empty:
        dao._drop_if_not_empty('tokens_aggregati',emozione)
    dao.aggregate(emozione)

