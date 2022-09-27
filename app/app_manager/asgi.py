import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import drink_consumption.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app_manager.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            drink_consumption.routing.websocket_urlpatterns
        )
    ),
})
