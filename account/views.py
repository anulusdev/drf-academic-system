from django.apps import apps
# from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import LecturerProfile, StudentProfile
from .permissions import IsOwnerOrReadOnly
from .serializers import LecturerSerializer, StudentSerializer


class StudentViewSet(ModelViewSet):
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    search_fields = ['level', 'course__title', 'department__name']
    ordering_fields = ['id', 'level']
    permission_classes = [IsOwnerOrReadOnly]
    # queryset = StudentProfile.objects.all()
    serializer_class = StudentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            raise PermissionDenied("Log in or Create an Account to view student profiles.")

        if not user.role:
            raise PermissionDenied("Make sure you have a role")

        if user.role == 'Student':
            return StudentProfile.objects.filter(user=user).select_related('department')
        if user.role == 'Lecturer':
            current_user = user.lecturerprofile
            his_department = current_user.department
            return StudentProfile.objects.filter(department=his_department)\
                .select_related('department')

    @action(detail=True)
    def me(self):
        student = StudentProfile.objects.filter(pk=self.request.user_id)
        serializer = StudentSerializer(student)
        return Response(serializer.data)


class LecturerViewSet(ModelViewSet):
    permission_classes = [IsOwnerOrReadOnly]
    serializer_class = LecturerSerializer

    def get_queryset(self):
        user = self.request.user
        department = apps.get_model('academics', 'Department')

        if user.is_anonymous:
            raise PermissionDenied("Log in or Create an Account to view lecturer profiles.")

        if not user.role:
            raise PermissionDenied("Make sure you have a role")

        if user.is_authenticated and user.role == 'Lecturer':
            current_user = user.lecturerprofile

            is_hod = department.objects.filter(hod=current_user).exists()
            if is_hod:
                hod_department = current_user.department
                return LecturerProfile.objects.filter(department=hod_department)\
                    .select_related('department')
            return LecturerProfile.objects.filter(user=user) \
                .select_related('department')
        if user.role == 'Student':
            raise PermissionDenied("You do not have permission to view lecturer profiles.")
