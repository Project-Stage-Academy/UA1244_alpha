from django.urls import path

from .views import CreateChatRoomView, SendMessageView, ListMessagesView

urlpatterns = [
    path('chatrooms/', CreateChatRoomView.as_view(), name='create-chatroom'),
    path('messages/', SendMessageView.as_view(), name='send-message'),
    path('chatrooms/<str:room_id>/messages/', ListMessagesView.as_view(), name='list-messages'),
]
