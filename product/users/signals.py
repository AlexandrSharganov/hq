from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from users.models import Balance

User = get_user_model()


@receiver(post_save, sender=User)
def save_or_create(sender, instance, created, **kwargs):
    """Создание баланса вместе с пользователем."""
    if created:
        Balance.objects.create(user=instance)
