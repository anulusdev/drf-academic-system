from django.contrib import admin
from .models import CustomUser, LecturerProfile, StudentProfile
from django.contrib.auth.admin import UserAdmin


@admin.register(CustomUser)
class AdminUser(UserAdmin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "usable_password", "password1",
                           "password2", "role", "first_name", "last_name"),
            },
        ),
    )
    list_display = ('id', "username", "email", "first_name", "last_name", "is_staff", "role")
    list_filter = ("is_staff", "is_superuser", "is_active", "role", "groups")


@admin.register(LecturerProfile)
class LecturerAdmin(admin.ModelAdmin):
    autocomplete_fields = ['user', 'department']
    list_display = ['first_name', 'last_name', 'department']
    list_editable = ['department']
    list_filter = ['department']
    list_select_related = ['user']
    search_fields = ['department']


@admin.register(StudentProfile)
class StudentAdmin(admin.ModelAdmin):
    autocomplete_fields = ['user', 'course', 'department']
    list_display = ['first_name', 'level', 'course_title', 'department']
    list_editable = ['department']
    list_select_related = ['user']

    @admin.display(description='Courses')
    def course_title(self, obj):
        return ", ".join([obj.course.title for obj in obj.enrollments.all()])
