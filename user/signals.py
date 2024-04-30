from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Student, Teacher


@receiver(post_save, sender=Teacher)
def notify_admin(sender, instance, created, **kwargs):
    print(instance)
    if created:
        print('A student has been created!')
    else:
        print('Updated')
