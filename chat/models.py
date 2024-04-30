from django.db import models

from user.models import Account


class Room(models.Model):
    ROOM_TYPE_CHOOSES = (
        (1, 'Student'),
        (2, 'Teacher'),
        (3, 'HOD'),
    )
    name = models.CharField(max_length=128, unique=True)
    type = models.PositiveIntegerField(choices=ROOM_TYPE_CHOOSES)
    online = models.ManyToManyField(to=Account, blank=True, related_name='users_online')
    created_by = models.ForeignKey(Account, on_delete=models.CASCADE)

    def get_online_count(self):
        return self.online.count()

    def join(self, user):
        self.online.add(user)
        self.save()

    def leave(self, user):
        self.online.remove(user)
        self.save()


class Message(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    content = models.CharField(max_length=512)
    timestamp = models.DateTimeField(auto_now_add=True)

