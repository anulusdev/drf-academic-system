from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    LECTURER = 'Lecturer', 'lecturer_role'
    STUDENT = 'Student', 'student_role'


class CustomUser(AbstractUser):
    username = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20, 
        choices=UserRole.choices, 
        default=UserRole.STUDENT
    )

    @property
    def is_lecturer(self):
        return self.role == UserRole.LECTURER

    @property
    def is_student(self):
        return self.role == UserRole.STUDENT

    @property
    def profile(self):
        """Automatically returns the correct profile based on role"""
        if self.is_lecturer:
            return getattr(self, 'lecturerprofile')
        if self.is_student:
            return getattr(self, 'studentprofile')
        return None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.username


class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session = models.ForeignKey('academics.AcademicSession', on_delete=models.DO_NOTHING, null=True)
    level = models.IntegerField(null=True, blank=True)

    department = models.ForeignKey(
        'academics.Department', null=True,
        blank=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name

    @admin.display(ordering='user__last_name')
    def last_name(self):
        return self.user.last_name


class LecturerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    department = models.ForeignKey(
        'academics.Department', null=True,
        blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name

    @admin.display(ordering='user__last_name')
    def last_name(self):
        return self.user.last_name
