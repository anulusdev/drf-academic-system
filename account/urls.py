from rest_framework.routers import DefaultRouter
from rest_framework import routers
from django.urls import path, include
from . import views


router = routers.DefaultRouter()
router.register('students', views.StudentViewSet, basename='students')
router.register('lecturers', views.LecturerViewSet, basename='lecturers')

urlpatterns = router.urls
