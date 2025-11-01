# drivers/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Driver

@receiver(post_save, sender=Driver)
def create_driver_user(sender, instance, created, **kwargs):
    if created and not instance.user:
        user = User.objects.create_user(
            username=f"driver_{instance.id}",
            password="default123",
        )
        instance.user = user
        instance.save()
