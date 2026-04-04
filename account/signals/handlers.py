from django.conf import settings
from django.db import transaction
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from account.models import LecturerProfile, StudentProfile

@receiver(pre_save, sender=settings.AUTH_USER_MODEL)
def capture_old_role(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_role = sender.objects.get(pk=instance.pk).role
        except sender.DoesNotExist:
            instance._old_role = None
    else:
        instance._old_role = None


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def sync_profile_on_save(sender, created, instance, update_fields, **kwargs):
    if update_fields is not None and update_fields == frozenset({'last_login'}):
        return

    if created:
        if instance.is_student:
            StudentProfile.objects.get_or_create(user=instance)
        elif instance.is_lecturer:
            LecturerProfile.objects.get_or_create(user=instance)
        return

    old_role = getattr(instance, '_old_role', None)

    if old_role == instance.role:
        return

    handle_profile_transition(instance, old_role)


def handle_profile_transition(user, old_role):
    with transaction.atomic():
        if user.is_student:
            LecturerProfile.objects.filter(user=user).update(is_active=False)
            StudentProfile.objects.get_or_create(user=user)

        elif user.is_lecturer:
            StudentProfile.objects.filter(user=user).update(is_active=False)
            LecturerProfile.objects.get_or_create(user=user)

