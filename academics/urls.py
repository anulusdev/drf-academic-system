
from rest_framework.routers import DefaultRouter
from rest_framework import routers
from django.urls import path, include
from . import views


router = routers.DefaultRouter()
router.register('courses', views.CourseViewSet, basename='courses')
router.register('department', views.DepartmentViewSet, basename='department')

urlpatterns = router.urls
