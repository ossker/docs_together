import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

class DocumentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from .models import Document, ChatMessage
        self.doc_id = self.scope['url_route']['kwargs']['doc_id']
        self.room_group_name = f'doc_{self.doc_id}'
        self.username = self.scope["user"].first_name or self.scope["user"].email

        if not hasattr(self.channel_layer, "presence"):
            self.channel_layer.presence = {}

        if self.room_group_name not in self.channel_layer.presence:
            self.channel_layer.presence[self.room_group_name] = set()

        self.channel_layer.presence[self.room_group_name].add(self.username)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        await self.send_presence_update()

    async def broadcast(self, event):
        await self.send(text_data=json.dumps(event))

    async def send_presence_update(self):
        users = list(self.channel_layer.presence[self.room_group_name])
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "broadcast",
                "message_type": "presence",
                "users": users,
            }
        )

    async def disconnect(self, close_code):
        if self.room_group_name in self.channel_layer.presence:
            self.channel_layer.presence[self.room_group_name].discard(self.username)

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.send_presence_update()

    async def receive(self, text_data):
        from .models import Document, ChatMessage
        data = json.loads(text_data)
        msg_type = data.get('type')
        content = data.get('content', '').strip()
        if msg_type == 'chat' and content:

            document = await database_sync_to_async(Document.objects.get)(id=self.doc_id)
            user = self.scope['user']

            await database_sync_to_async(ChatMessage.objects.create)(
                document=document,
                user=user,
                content=content
            )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_to_group',
                'user': self.scope['user'].first_name or self.scope['user'].email_address,
                'message_type': msg_type,
                'content': data['content'],
            }
        )

    async def send_to_group(self, event):
        await self.send(text_data=json.dumps({
            'message_type': event['message_type'],
            'user': event.get('user', ''),
            'content': event['content'],
        }))