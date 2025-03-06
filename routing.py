from django.urls import re_path

from card import consumers

websocket_urlpatterns = [
    re_path(r'ws/card/(?P<room_uuid>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
