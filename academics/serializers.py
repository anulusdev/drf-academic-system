from common.seriliazers import SimpleDepartment, SimpleLecturer
from rest_framework import serializers
from .models import *


class DepartmentSerializer(serializers.ModelSerializer):
    hod = SimpleLecturer()

    class Meta:
        model = Department
        fields = ['id', 'name', 'hod']


class DepartmentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ['id', 'name', 'hod']


class CourseSerializer(serializers.ModelSerializer):
    department = SimpleDepartment()
    lecturer = SimpleLecturer()

    class Meta:
        model = Course
        fields = ['id', 'title', 'code', 'unit', 'department', 'lecturer']


class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['title', 'unit', 'department', 'lecturer']
