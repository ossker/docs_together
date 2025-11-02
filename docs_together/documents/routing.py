from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/doc/(?P<doc_id>[0-9a-fA-F-]+)/$", consumers.DocumentConsumer.as_asgi()),
]