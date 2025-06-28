import json

from asgiref.sync import async_to_sync
from collections import deque
from channels.generic.websocket import WebsocketConsumer

from .models import Room, User

from .room import Rooms

from django.contrib.auth.models import AnonymousUser

from . import deck
from .manager import RoomManager

import ast

manager = RoomManager()


class ChatConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_uuid = None
        self.room_name = None
        self.room_group_name = None
        self.room = None
        self.user = None
        self.cards = None
        self.session_id = None

    def connect(self):

        # global player

        self.room_uuid = self.scope['url_route']['kwargs']['room_uuid']
        self.session_id = self.scope['headers'][8][1].decode('utf-8')
        print(self.scope['headers'][8][1].decode('utf-8'))

        # print(self.scope['headers'])
        # print(self.session_id)
        manager.join(self.session_id, self.room_uuid)
        cards = User.objects.values('cards').filter(session=self.session_id).get()
        self.cards = ast.literal_eval(cards['cards'])

        self.room_group_name = f'chat_{self.room_uuid}'
        self.room = Room.objects.get(roomId=self.room_uuid)
        self.user = AnonymousUser

        # join the room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'player_joined': len(manager.get_players(self.room_uuid)),
                'total_player': self.room.playerCount,
                'start_game': self.room.playerCount == len(manager.get_players(self.room_uuid))
            }
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        card = ast.literal_eval(text_data_json['card'])
        print(card)
        if manager.get_first_player(self.room_uuid) is None:
            if '3C' in card:
                if all(x in self.cards for x in card):
                    # Setting first player
                    manager.set_first_player(self.room_uuid, self.session_id)

                    # Setting number of cards dealed
                    manager.set_number_of_card_dealed(self.room_uuid, len(card))

                    manager.set_turns(self.room_uuid, card)

                    # Remove the card dealed.
                    self.cards = list(set(self.cards) - set(card))
                    if manager.get_players(self.room_uuid).index(manager.get_first_player(self.room_uuid)) == 0:
                        manager.next_player(self.room_uuid)
                    async_to_sync(self.channel_layer.group_send)(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'current_player': self.session_id,
                            'next_player': manager.get_players(self.room_uuid)[0],
                            # 'number_of_card_dealed': manager.get_number_of_card_dealed(self.room_uuid),
                            'cards': manager.get_turns(self.room_uuid)
                        }
                    )
                else:
                    async_to_sync(self.channel_layer.group_send)(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'current_player': self.session_id,
                            # 'next_player': manager.get_players(self.room_uuid)[0],
                            'cards': manager.get_turns(self.room_uuid),
                            # 'number_of_card_dealed': manager.get_number_of_card_dealed(self.room_uuid),
                            'error': "You don't have that card!"
                        }
                    )
            else:
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'current_player': self.session_id,
                        # 'next_player': manager.get_players(self.room_uuid)[0],
                        'error': 'first card should be 3C'
                    }
                )

        else:
            position_of_current_card = None
            position_of_previous_card = None
            if self.session_id == manager.get_players(self.room_uuid)[0]:
                if len(card) == 1 and 'pass' in card:
                    manager.next_player(self.room_uuid)
                    async_to_sync(self.channel_layer.group_send)(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'current_player': self.session_id,
                            'next_player': manager.get_players(self.room_uuid)[0],
                            'number_of_card_dealed': manager.get_number_of_card_dealed(self.room_uuid),
                            'cards': manager.get_turns(self.room_uuid),
                            'message': f'Player {self.session_id} passed his turn.'
                        }
                    )
                else:
                    if manager.get_turns(self.room_uuid):
                        previous_card = manager.get_turns(self.room_uuid)[-1][0][0] if len(
                            manager.get_turns(self.room_uuid)) > 0 else None
                        position_of_previous_card = deck.RANKS.index(previous_card) if previous_card is not None else -1
                        position_of_current_card = deck.RANKS.index(card[0][0])
                    else:
                        manager.set_number_of_card_dealed(self.room_uuid, len(card))

                    if not manager.get_turns(self.room_uuid) or position_of_current_card >= position_of_previous_card:
                        if all(x in self.cards for x in card):
                            if len(card) == 1 and card[0][0] == '2':
                                self.cards = list(set(self.cards) - set(card))
                                manager.set_turns(self.room_uuid)
                                async_to_sync(self.channel_layer.group_send)(
                                    self.room_group_name,
                                    {
                                        'type': 'chat_message',
                                        'current_player': self.session_id,
                                        'next_player': manager.get_players(self.room_uuid)[0],
                                        'number_of_card_dealed': manager.get_number_of_card_dealed(self.room_uuid),
                                        'cards': manager.get_turns(self.room_uuid),
                                        'message': f'Player {self.session_id} cleared this turn.'
                                    }
                                )
                            else:
                                if manager.get_number_of_card_dealed(self.room_uuid) == len(card):
                                    if all(c[0] == card[0][0] for c in card):
                                        manager.set_number_of_card_dealed(self.room_uuid, len(card))
                                        manager.set_turns(self.room_uuid, card)
                                        self.cards = list(set(self.cards) - set(card))
                                        manager.next_player(self.room_uuid)
                                        async_to_sync(self.channel_layer.group_send)(
                                            self.room_group_name,
                                            {
                                                'type': 'chat_message',
                                                'current_player': self.session_id,
                                                'next_player': manager.get_players(self.room_uuid)[0],
                                                'number_of_card_dealed': manager.get_number_of_card_dealed(
                                                    self.room_uuid),
                                                'cards': manager.get_turns(self.room_uuid)
                                            }
                                        )
                                    else:
                                        async_to_sync(self.channel_layer.group_send)(
                                            self.room_group_name,
                                            {
                                                'type': 'chat_message',
                                                'current_player': self.session_id,
                                                'cards': manager.get_turns(self.room_uuid),
                                                'number_of_card_dealed': manager.get_number_of_card_dealed(
                                                    self.room_uuid),
                                                'error': 'Cards you dealed are not same'
                                            }
                                        )

                                else:
                                    async_to_sync(self.channel_layer.group_send)(
                                        self.room_group_name,
                                        {
                                            'type': 'chat_message',
                                            'current_player': self.session_id,
                                            'cards': manager.get_turns(self.room_uuid),
                                            'number_of_card_dealed': manager.get_number_of_card_dealed(self.room_uuid),
                                            'error': f'You should deal {manager.get_number_of_card_dealed(self.room_uuid)} cards'
                                        }
                                    )
                        else:
                            async_to_sync(self.channel_layer.group_send)(
                                self.room_group_name,
                                {
                                    'type': 'chat_message',
                                    'current_player': self.session_id,
                                    'next_player': manager.get_players(self.room_uuid)[0],
                                    'cards': manager.get_turns(self.room_uuid),
                                    'number_of_card_dealed': manager.get_number_of_card_dealed(self.room_uuid),
                                    'error': "You don't have that card!"
                                }
                            )
                    else:
                        async_to_sync(self.channel_layer.group_send)(
                            self.room_group_name,
                            {
                                'type': 'chat_message',
                                'current_player': self.session_id,
                                'cards': manager.get_turns(self.room_uuid),
                                'number_of_card_dealed': manager.get_number_of_card_dealed(self.room_uuid),
                                'error': "Your card is lower in rank than pervious card"
                            }
                        )
            else:
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'current_player': self.session_id,
                        'next_player': manager.get_players(self.room_uuid)[0],
                        'cards': manager.get_turns(self.room_uuid),
                        'number_of_card_dealed': manager.get_number_of_card_dealed(self.room_uuid),
                        'error': "Not your turn!"
                    }
                )

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))
