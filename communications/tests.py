from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase
from django.contrib.auth.models import AnonymousUser
from investors.models import InvestorProfile
from startups.models import StartUpProfile
from users.models import User
from .consumers import ChatConsumer
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .di_container import init_container
from .domain.entities.messages import ChatRoom, Message


class ChatConsumerTest(TransactionTestCase):

    async def asyncSetUp(self):

        self.user1 = await database_sync_to_async(User.objects.create_user)(
            email="johnson@gmail.com",
            password="123456pok&*gebBCBDHD_t4ng",
            first_name="John",
            last_name="Doe",
            user_phone="+1234567890"
        )
        await database_sync_to_async(self.user1.add_role)('Investor')

        self.user2 = await database_sync_to_async(User.objects.create_user)(
            email="linel@gmail.com",
            password="12345qfenjoubfjkUHEFWHF9_6pok",
            first_name="Lim",
            last_name="Non",
            user_phone="+1234567890"
        )
        await database_sync_to_async(self.user2.add_role)('Startup')

        await database_sync_to_async(InvestorProfile.objects.create)(user=self.user1)

        self.chat_name = 'test_chat_room'

    async def get_communicator(self, user):
        communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), f"/ws/chat/{self.chat_name}/")
        communicator.scope['user'] = user
        communicator.scope['url_route'] = {'kwargs': {'room_name': self.chat_name}}
        return communicator

    async def test_create_chat_room(self):
        await self.asyncSetUp()

        chat_room = ChatRoom(room_id=self.chat_name, startup_id=self.user1.id, investor_id=self.user2.id)
        await database_sync_to_async(mongo_container.create_chatroom)(chat_room)

        created_chat_room = await database_sync_to_async(mongo_container.get_chatroom)(self.chat_name)
        self.assertIsNotNone(created_chat_room, "Chat room was not created successfully.")

    async def test_connect_to_chat(self):
        await self.asyncSetUp()

        communicator = await self.get_communicator(self.user1)
        connected, _ = await communicator.connect()
        assert connected, "Failed to connect to the chat."

    async def test_connect_unauthenticated_user(self):
        await self.asyncSetUp()

        communicator = await self.get_communicator(AnonymousUser())
        connected, _ = await communicator.connect()
        self.assertFalse(connected, "Unauthenticated user was able to connect to the chat.")

        await communicator.disconnect()

    async def test_receive_message(self):
        await self.asyncSetUp()

        communicator1 = await self.get_communicator(self.user1)
        communicator2 = await self.get_communicator(self.user2)
        connected1, _ = await communicator1.connect()
        self.assertTrue(connected1, "Failed to connect user1 to the chat.")
        connected2, _ = await communicator2.connect()
        self.assertTrue(connected2, "Failed to connect user2 to the chat.")

        investor_profile, created = await database_sync_to_async(InvestorProfile.objects.get_or_create)(user=self.user1)
        startup_profile, created = await database_sync_to_async(StartUpProfile.objects.get_or_create)(user_id=self.user2)

        messages = [
            {'message': 'Hello!', 'sender_id': investor_profile.id, 'receiver_id': startup_profile.id},
            {'message': 'How are You?', 'sender_id': investor_profile.id, 'receiver_id': startup_profile.id},
            ]

        for message in messages:
            await communicator1.send_json_to(message)

        for message in messages:
            response = await communicator2.receive_json_from()
            self.assertEqual(response['message'], message['message'], "Message received does not match sent message.")
            self.assertEqual(response['sender_id'], message['sender_id'], "Sender ID does not match.")
            self.assertEqual(response['receiver_id'], message['receiver_id'], "Receiver ID does not match.")

        await communicator1.disconnect()
        await communicator2.disconnect()

    async def test_send_empty_message(self):
        await self.asyncSetUp()

        communicator1 = await self.get_communicator(self.user1)
        communicator2 = await self.get_communicator(self.user2)
        connected1, _ = await communicator1.connect()
        self.assertTrue(connected1, "Failed to connect user1 to the chat.")
        connected2, _ = await communicator2.connect()
        self.assertTrue(connected2, "Failed to connect user2 to the chat.")

        investor_profile, created = await database_sync_to_async(InvestorProfile.objects.get_or_create)(user=self.user1)
        startup_profile, created = await database_sync_to_async(StartUpProfile.objects.get_or_create)(user_id=self.user2)

        message = {
            'message': '',
            'sender_id': investor_profile.id,
            'receiver_id': startup_profile.id,
        }

        await communicator1.send_json_to(message)

        response = await communicator1.receive_json_from()
        self.assertEqual(response['error'], 'Message cannot be empty.', "Error message was not received for empty message.")

        await communicator1.disconnect()
        await communicator2.disconnect()


class ChatRoomTests(APITestCase):
    container = init_container()
    mongo_repo = container.resolve(MongoDBRepository)

    def test_create_chat_room(self):
        url = reverse('create-chatroom')
        data = {
            'room_id': 'valid_room_id',
            'startup_id': 1,
            'investor_id': 2,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('room_id', response.data)

    def test_create_chat_room_invalid_data(self):
        url = reverse('create-chatroom')
        data = {}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MessageTests(APITestCase):
    container = init_container()
    mongo_repo = container.resolve(MongoDBRepository)

    def setUp(self):
        self.chat_room = ChatRoom(room_id='valid_room_id', startup_id=1, investor_id=2, messages=[])
        self.mongo_repo.create_chatroom(self.chat_room)

    def test_send_message(self):
        url = reverse('send-message', args=[self.chat_room.room_id])
        data = {
            'sender_id': 1,
            'receiver_id': 2,
            'content': 'Hello!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message_id', response.data)

    def test_send_message_invalid_chat_room(self):
        url = reverse('send-message', args=['invalid_room_id'])
        data = {
            'sender_id': 1,
            'receiver_id': 2,
            'content': 'Hello!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_messages(self):
        message = Message(sender_id=1, receiver_id=2, content='Hello!')
        self.mongo_repo.add_message(self.chat_room.room_id, message)

        url = reverse('list-messages', args=[self.chat_room.room_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_list_messages_invalid_chat_room(self):
        url = reverse('list-messages', args=['invalid_room_id'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
