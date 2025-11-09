import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

class DocumentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from .models import Document, ChatMessage
        self.doc_id = self.scope['url_route']['kwargs']['doc_id']
        self.room_group_name = f'doc_{self.doc_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

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