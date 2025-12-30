from django.contrib import admin
from .models import *


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    autocomplete_fields = ['lecturer']
    list_display = ['title', 'code', 'unit', 'department', 'lecturer']
    list_editable = ['unit', 'lecturer']
    list_filter = ['lecturer', 'unit']
    list_select_related = ['department', 'lecturer']
    search_fields = ['title', 'code', 'unit', 'department', 'lecturer']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    autocomplete_fields = ['hod']
    list_display = ['name', 'hod']
    search_fields = ['name']


admin.site.register(AcademicSession)
