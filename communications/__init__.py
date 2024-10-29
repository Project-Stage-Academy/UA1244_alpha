import logging
from functools import lru_cache
from django.conf import settings
from punq import Container
from pymongo import MongoClient

from communications.events.base import BaseEvent
from communications.events.messages import MessageNotificationEvent
from communications.repositories.mongo import MongoDBRepository
from communications.services.messages import CreateChatCommand, CreateMessageCommand


logger = logging.getLogger('django')

@lru_cache(1)
def init_container() -> Container:
    container = Container()

    def init_mongo_client() -> MongoClient:
        try:
            client = MongoClient(settings.MONGO_URI)
            logger.info(f"Successfully connected to MongoDB at {settings.MONGO_URI}")
            return client
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def init_mongo_repository() -> MongoDBRepository:
        try:
            repository = MongoDBRepository(
                mongo_db_client=container.resolve(MongoClient),
                mongo_db_db_name=settings.MONGO_DB_NAME,
                mongo_db_collection_name=settings.MONGO_COLLECTION_NAME
            )
            logger.info("MongoDBRepository successfully initialized.")
            return repository
        except Exception as e:
            logger.error(f"Failed to initialize MongoDBRepository: {e}")
            raise


    def init_create_chat_command(repo: MongoDBRepository) -> CreateChatCommand:
        return CreateChatCommand(mongo_repo=repo)


    def init_send_message_command(repo: MongoDBRepository, notification: BaseEvent) -> CreateMessageCommand:
        return CreateMessageCommand(mongo_repo=repo, messege_event=notification)

    container.register(BaseEvent, MessageNotificationEvent)

    container.register(MongoClient, factory=init_mongo_client)
    container.register(MongoDBRepository, factory=init_mongo_repository)

    container.register(CreateChatCommand, factory=lambda: init_create_chat_command(container.resolve(MongoDBRepository)))
    container.register(
        CreateMessageCommand,
        factory=lambda: init_send_message_command(
            container.resolve(MongoDBRepository),
            container.resolve(BaseEvent)
    ))

    return container
