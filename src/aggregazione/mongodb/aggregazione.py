from src.dao.mongodb_dao import *
from src.utils import config


def aggregazione(dao:MongoDBDAO,emozione, drop_if_not_empty=None):
    if drop_if_not_empty:
        dao._drop_if_not_empty('tokens_aggregati',emozione)
    dao.aggregate(emozione)

def test_aggregate_mongo(mongo_dao:MongoDBDAO,drop_if_not_empty=False):
    aggregazione(mongo_dao,'anger',drop_if_not_empty)

if __name__ == '__main__':
    dao=mongodb_dao.MongoDAO(config.MONGO_CONFIG)
    test_aggregate_mongo(dao,True)

