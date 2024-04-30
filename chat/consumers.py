import json

from asgiref.sync import async_to_sync

from channels.generic.websocket import WebsocketConsumer

from .models import Room, Message


class ChatConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_name = None
        self.room_group_name = None
        self.room = None
        self.user = None

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.room = Room.objects.get(name=self.room_name)
        self.user = self.scope['user']

        if self.room.type == 1:
            type_list = [1, 2, 3, 4]
            if self.user.user_type in type_list:
                self.accept()
        elif self.room.type == 2:
            type_list = [2, 3, 4]
            if self.user.user_type in type_list:
                self.accept()
        elif self.room.type == 3:
            type_list = [3, 4]
            if self.user.user_type in type_list:
                self.accept()
        # connection has to be accepted
        # if self.user.user_type == self.room.type:
        #     self.accept()

        # print(self.user.user_type, self.room.type)
        # join the room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        print(text_data_json)
        if not self.user.is_authenticated:
            return

        # send chat message event to the room
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'user': self.user.name,
                'message': message,
            }
        )

        Message.objects.create(user=self.user, room=self.room, content=message)

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))
