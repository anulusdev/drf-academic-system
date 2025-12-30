from common.seriliazers import SimpleDepartment, SimpleCourse
from djoser.serializers import (
    UserSerializer as BaseUserSerializer,
    UserCreateSerializer as BaseUserCreateSerializer
)
from rest_framework import serializers
from .models import *


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'username', 'password', 'email', 'role', 'first_name', 'last_name']


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'username', 'role', 'email', 'first_name', 'last_name']


class SimpleUser(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email']


class StudentSerializer(serializers.ModelSerializer):
    department = SimpleDepartment()

    class Meta:
        model = StudentProfile
        fields = ['id', 'first_name', 'level', 'department']


class LecturerSerializer(serializers.ModelSerializer):
    department = SimpleDepartment()

    class Meta:
        model = LecturerProfile
        fields = ['id', 'user', 'first_name', 'last_name', 'department']
