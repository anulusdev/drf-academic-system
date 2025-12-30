from rest_framework import serializers
from academics.models import *
from account.models import *


class SimpleCourse(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['title']


class SimpleDepartment(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['name']


class SimpleLecturer(serializers.ModelSerializer):
    class Meta:
        model = LecturerProfile
        fields = ['first_name']
