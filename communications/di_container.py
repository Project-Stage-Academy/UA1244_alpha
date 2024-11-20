import logging
from functools import lru_cache
from django.conf import settings
from punq import Container, Scope
from pymongo import MongoClient

from communications.events.base import BaseEvent
from communications.events.messages import MessageNotificationEvent
from communications.repositories.base import BaseMessagesRepository, BaseChatsRepository
from communications.repositories.mongo import MongoDBChatsRepositories, MongoDBMessagesRepositories
from communications.services.commands.messages import CreateChatCommand, CreateMessageCommand
from communications.services.queries.messages import ChatRoomQuery, MessageQuery

logger = logging.getLogger('django')


@lru_cache(1)
def init_container() -> Container:
    container = Container()

    # Initialize MongoDB client
    def init_mongo_client() -> MongoClient:
        try:
            client = MongoClient(settings.MONGO_URI)
            logger.info(f"Successfully connected to MongoDB at {settings.MONGO_URI}")
            return client
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    container.register(MongoClient, factory=init_mongo_client, scope=Scope.singleton)

    # Register repositories
    def init_mongo_chats_repository() -> MongoDBChatsRepositories:
        return MongoDBChatsRepositories(
            mongo_db_client=container.resolve(MongoClient),
            mongo_db_db_name=settings.MONGO_DB_NAME,
            mongo_db_collection_name=settings.MONGO_COLLECTION_NAME
        )

    def init_mongo_messages_repository() -> MongoDBMessagesRepositories:
        return MongoDBMessagesRepositories(
            mongo_db_client=container.resolve(MongoClient),
            mongo_db_db_name=settings.MONGO_DB_NAME,
            mongo_db_collection_name=settings.MONGO_COLLECTION_NAME
        )

    container.register(BaseChatsRepository, factory=init_mongo_chats_repository, scope=Scope.singleton)
    container.register(BaseMessagesRepository, factory=init_mongo_messages_repository, scope=Scope.singleton)

    # Register events
    container.register(BaseEvent, MessageNotificationEvent)

    # Register commands
    def init_create_chat_command() -> CreateChatCommand:
        return CreateChatCommand(mongo_repo=container.resolve(BaseChatsRepository))

    def init_send_message_command() -> CreateMessageCommand:
        return CreateMessageCommand(
            mongo_repo=container.resolve(BaseMessagesRepository),
            messege_event=container.resolve(BaseEvent),
            chat_query=container.resolve(ChatRoomQuery),
        )

    container.register(CreateChatCommand, factory=init_create_chat_command)
    container.register(CreateMessageCommand, factory=init_send_message_command)

    # Register queries
    def init_get_chat_room_query() -> ChatRoomQuery:
        return ChatRoomQuery(mongo_repo=container.resolve(BaseChatsRepository))

    def init_get_message_query() -> MessageQuery:
        return MessageQuery(mongo_repo=container.resolve(BaseMessagesRepository))

    container.register(ChatRoomQuery, factory=init_get_chat_room_query)
    container.register(MessageQuery, factory=init_get_message_query)

    return container
