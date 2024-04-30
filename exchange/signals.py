from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Question


@receiver(post_save, sender=Question)
def notify_admin(sender, instance, created, **kwargs):
    print(instance)
    if created:
        print('A question has been created!')
    else:
        print('Updated')
