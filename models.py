import uuid
import shortuuid
from shortuuid.django_fields import ShortUUIDField

from django.db import models


# Create your models here.
class Room(models.Model):
    roomId = models.CharField(max_length=22, default=shortuuid.uuid, editable=False, unique=True, primary_key=True)
    playerCount = models.IntegerField()
    cards = models.TextField(null=True)  # JSON-serialized (text) version of your list

    # online = models.ManyToManyField(to=Account, blank=True, related_name='users_online')
    # created_by = models.ForeignKey(Account, on_delete=models.CASCADE)

    def get_online_count(self):
        return self.online.count()

    def join(self, user):
        self.online.add(user)
        self.save()

    def leave(self, user):
        self.online.remove(user)
        self.save()

    def __str__(self):
        roomId = str(self.roomId)
        return roomId.replace('-', "")


class User(models.Model):
    uuid = models.CharField(default=shortuuid.uuid, editable=False, unique=True, primary_key=True, max_length=20)
    session = models.CharField(max_length=500, unique=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    cards = models.TextField(null=True)  # JSON-serialized (text) version of your list
