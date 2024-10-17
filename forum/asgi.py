import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from communications.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forum.settings')

"""
ASGI application configuration.

This application routes HTTP requests to Django's ASGI application and WebSocket requests
to the appropriate consumer based on the defined URL patterns.

Attributes:
    application (ProtocolTypeRouter): The main ASGI application that handles routing.
"""

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
