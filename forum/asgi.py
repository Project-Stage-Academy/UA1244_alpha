import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from communications.middlewares import JWTAuthMiddlewareStack
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
    "websocket": JWTAuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
