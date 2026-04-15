from django.db import transaction
from .models import StudentProfile, LecturerProfile


class UserService:
    @staticmethod
    def switch_user_role(user):
        """
        Handles profile transition when a user's role changes.
        Soft-deletes the old profile, creates the new one.
        Called explicitly from views never from signals.
        """
        with transaction.atomic():
            if user.is_student:
                LecturerProfile.objects.filter(user=user).update(is_active=False)
                StudentProfile.objects.get_or_create(user=user)

            elif user.is_lecturer:
                StudentProfile.objects.filter(user=user).update(is_active=False)
                LecturerProfile.objects.get_or_create(user=user)

    @staticmethod
    def create_profile_for_new_user(user):
        """
        Creates the correct profile when a brand new user is registered.
        Called explicitly after user creation.
        """
        with transaction.atomic():
            if user.is_student:
                StudentProfile.objects.get_or_create(user=user)
            elif user.is_lecturer:
                LecturerProfile.objects.get_or_create(user=user)