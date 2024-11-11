from django.urls import path

from .views import CreateChatRoomView, SendMessageView, ListMessagesView, ListUserChatsView

urlpatterns = [
    path('chatrooms/', CreateChatRoomView.as_view(), name='create-chatroom'),
    path('messages/<str:room_oid>/', SendMessageView.as_view(), name='send-message'),
    path('chatrooms/<str:room_oid>/messages/', ListMessagesView.as_view(), name='list-messages'),
    path('chatrooms/user_chats/', ListUserChatsView.as_view(), name='user-chats')
]
