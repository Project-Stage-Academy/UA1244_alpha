from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

User = get_user_model()


class ChatRoom(models.Model):
    """
        ChatRoom represents a room where a startup and an investor communicate.

        Attributes:
            investor (ForeignKey): The investor involved in the conversation.
            startup (ForeignKey): The startup involved in the conversation.
            created_at (DateTimeField): Timestamp when the chat room was created.
        """
    investor = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='investor_chatrooms')
    startup = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='startup_chatrooms')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('investor', 'startup')
        ordering = ['created_at']

    def clean(self):
        """
        Ensure that one user has role - Investor and the other user has role - Startup.
        """

        is_investor = self.investor.roles.filter(name="Investor").exists()
        is_startup = self.startup.roles.filter(name="Startup").exists()

        if not (is_investor and is_startup):
            raise ValidationError("One user must be an Investor, "
                                  "and the other user must be a Startup.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'ChatRoom between {self.investor} and {self.startup}'


class Message(models.Model):
    """
    A model for storing messages between startup and investor.

    Attributes:
    room (ForeignKey): The room where the investor and the startup are communicating.
    sender (ForeignKey): The user who sent the message.
    receiver (ForeignKey): The user who received the message.
    content (TextField): The text content of the message.
    sent_at (DateTimeField): The timestamp when the message was sent.
    read_at (DateTimeField): The timestamp when the message was read. Can be null if the message has not been read yet.
    """
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receive_messages")
    content = models.TextField(max_length=1000)
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['sent_at']

    def __str__(self):
        return f"Message from {self.sender.email} to {self.receiver.email}"

