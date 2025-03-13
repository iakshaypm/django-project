"""
ASGI config for president project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack

from card.middleware import TokenAuthMiddleware

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

from card import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'president.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

application = ProtocolTypeRouter({
  'http': get_asgi_application(),
  'websocket': URLRouter(
            routing.websocket_urlpatterns
        )
})
