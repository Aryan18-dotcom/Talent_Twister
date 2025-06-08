import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Chat, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

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
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user_id = self.scope['user'].id
        chat_id = self.room_name

        await self.save_message(chat_id, user_id, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user_id': user_id,
                'username': self.scope['user'].username,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        user_id = event['user_id']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'user_id': user_id,
        }))

    @database_sync_to_async
    def save_message(self, chat_id, user_id, content):
        chat = Chat.objects.get(id=chat_id)
        user = User.objects.get(id=user_id)
        Message.objects.create(chat=chat, sender=user, content=content)