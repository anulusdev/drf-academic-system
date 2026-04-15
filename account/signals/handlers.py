from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from account.services import UserService


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_on_registration(sender, created, instance, update_fields, **kwargs):
    if update_fields is not None and update_fields == frozenset({'last_login'}):
        return

    if created:
        UserService.create_profile_for_new_user(instance)
