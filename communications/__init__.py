from functools import lru_cache

from django.conf import settings
from punq import Container
from pymongo import MongoClient

from communications.repositories.mongo import MongoDBRepository


@lru_cache(1)
def init_container() -> Container:
    container = Container()

    def init_mongo_client() -> MongoClient:
        return MongoClient(settings.MONGO_URI)

    def init_mongo_repository() -> MongoDBRepository:
        return MongoDBRepository(
            mongo_db_client=container.resolve(MongoClient),
            mongo_db_db_name=settings.MONGO_DB_NAME,
            mongo_db_collection_name=settings.MONGO_COLLECTION_NAME
        )

    container.register(MongoClient, factory=init_mongo_client)
    container.register(MongoDBRepository, factory=init_mongo_repository)

    return container
