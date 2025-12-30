from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from account.models import LecturerProfile, StudentProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(created, instance, **kwargs):
    if created:
        if instance.role == 'Student':
            StudentProfile.objects.create(user=instance)
        if instance.role == 'Lecturer':
            LecturerProfile.objects.create(user=instance)
