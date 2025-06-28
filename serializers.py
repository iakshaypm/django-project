import ast

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Room, User


class RoomSerializer(serializers.ModelSerializer):
    roomId = serializers.CharField(read_only=True)
    playerCount = serializers.IntegerField(write_only=True)

    class Meta:
        model = Room
        fields = ['roomId', 'playerCount']


class UserSerializer(serializers.ModelSerializer):
    session = serializers.CharField(validators=[UniqueValidator(queryset=User.objects.all(), message='User already '
                                                                                                     'collected '
                                                                                                     'the cards.')])
    cards = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['room', 'session', 'cards']
        extra_kwargs = {'room': {'write_only': True}}

    def get_cards(self, obj):
        return obj.cards

    def validate(self, attrs):
        cards = Room.objects.values('cards').filter(roomId=str(attrs['room'])).get()
        cards = ast.literal_eval(cards['cards'])
        if not cards:
            raise serializers.ValidationError({'error': 'All cards of the room has been distributed.'})
        else:
            attrs['cards'] = cards.pop()
        Room.objects.filter(roomId=str(attrs['room'])).update(cards=cards)
        return attrs
