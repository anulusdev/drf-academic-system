import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def student_user(db):
    user = User.objects.create_user(
        username='teststudent',
        email='student@test.com',
        password='testpass123',
        role='Student',
        first_name='Test',
        last_name='Student'
    )
    return user


@pytest.fixture
def lecturer_user(db):
    user = User.objects.create_user(
        username='testlecturer',
        email='lecturer@test.com',
        password='testpass123',
        role='Lecturer',
        first_name='Test',
        last_name='Lecturer'
    )
    return user


@pytest.fixture
def admin_user(db):
    user = User.objects.create_superuser(
        username='admin',
        email='admin@test.com',
        password='adminpass123',
    )
    return user


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def student_client(api_client, student_user):
    api_client.force_authenticate(user=student_user)
    return api_client


@pytest.fixture
def lecturer_client(api_client, lecturer_user):
    api_client.force_authenticate(user=lecturer_user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client