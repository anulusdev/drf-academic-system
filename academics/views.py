from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .models import Course, Department, Enrollment
from .permissions import IsAdminOrReadOnly, IsHodOrReadOnly, IsStudent
from .serializers import (
    CourseSerializer, CourseCreateSerializer, 
    DepartmentSerializer, DepartmentCreateSerializer
)

class CourseViewSet(ModelViewSet):
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    search_fields = ['code', 'unit', 'department__name', 'lecturer__user__first_name']
    ordering_fields = ['id', 'unit', ]
    queryset = Course.objects.all().select_related('department')

    def get_permissions(self):
        user = self.request.user

        if user.is_authenticated and user.role == 'Lecturer':
            return [IsHodOrReadOnly()]
        return [IsAdminOrReadOnly()]

    @action(detail=True, permission_classes=[IsAuthenticated])
    def allocate(self, request, pk=None):
        user = request.user
        lecturer = user.lecturerprofile
        course = self.get_object()

        if user.role != 'Lecturer':
            return Response(
                {'detail': 'Only User with Lecturer Profile can allocate courses'},
                status=status.HTTP_403_FORBIDDEN
            )
        if lecturer.department != course.department:
            return Response(
                {'detail': 'Course not in your department'},
                status=status.HTTP_403_FORBIDDEN
            )
        if course.lecturer == lecturer:
            return Response(
                {'detail': 'You have already ben allocated for this course'},
                status=status.HTTP_400_BAD_REQUEST
            )

        course.lecturer = lecturer
        course.save()
        return Response({
            "status": "Allocation Successful",
            "course": course.code,
            "assigned_to": f"{lecturer.user.first_name} {lecturer.user.last_name}"
        })

    @action(detail=True, permission_classes=[IsStudent, IsAuthenticated])
    def enroll(self, request, pk=None):
        user = request.user
        if user.role != 'Student':
            return Response(
                {'detail': 'Only User with Student Profile can enroll'},
                status=status.HTTP_403_FORBIDDEN
            )
        student = user.studentprofile
        course = self.get_object()

        if student.department != course.department:
            return Response(
                {'detail': 'Course not in your department'},
                status=status.HTTP_403_FORBIDDEN
            )

        if Enrollment.objects.filter(
                student=student,
                course=course
        ).exists():
            return Response(
                {'detail': 'You have already enrolled for this course'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Enrollment.objects.create(
            student=student,
            course=course
        )
        return Response(
            {'detail': 'Successfully enrolled.'},
            status=status.HTTP_201_CREATED
        )

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT']:
            return CourseCreateSerializer
        return CourseSerializer


class DepartmentViewSet(ModelViewSet):
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    search_fields = ['name', 'hod__user__first_name', 'description',]
    ordering_fields = ['id', 'name']
    queryset = Department.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT']:
            return DepartmentCreateSerializer
        return DepartmentSerializer

    def get_permissions(self):
        user = self.request.user

        if user.is_authenticated and user.role == 'Lecturer':
            return [IsHodOrReadOnly()]
        return [IsAdminOrReadOnly()]
