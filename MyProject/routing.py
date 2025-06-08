# MyProject/routing.py
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from Myapp import routing as myapp_routing  # Import Myapp's routing
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MyProject.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            myapp_routing.websocket_urlpatterns  # Include Myapp's WebSocket routes
        )
    ),
})