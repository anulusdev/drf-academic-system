import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from django.urls import reverse
from account.models import StudentProfile, LecturerProfile

User = get_user_model()


# ── PROFILE CREATION TESTS ─────────────────────────────────

class TestProfileAutoCreation:

    def test_student_user_gets_student_profile(self, student_user):
        """
        When a user with role=Student is created, a StudentProfile
        must be automatically created by the post_save signal.
        """
        assert StudentProfile.objects.filter(user=student_user).exists()

    def test_lecturer_user_gets_lecturer_profile(self, lecturer_user):
        """
        When a user with role=Lecturer is created, a LecturerProfile
        must be automatically created.
        """
        assert LecturerProfile.objects.filter(user=lecturer_user).exists()

    def test_student_does_not_get_lecturer_profile(self, student_user):
        """
        A student must NOT have a LecturerProfile created.
        This guards against the signal creating the wrong profile type.
        """
        assert not LecturerProfile.objects.filter(user=student_user).exists()

    def test_lecturer_does_not_get_student_profile(self, lecturer_user):
        """
        A lecturer must NOT have a StudentProfile created.
        """
        assert not StudentProfile.objects.filter(user=lecturer_user).exists()


# ── STUDENT VIEWSET TESTS ──────────────────────────────────

class TestStudentViewSet:

    def test_student_can_only_see_own_profile(
        self, student_client, student_user, db
    ):
        """
        The get_queryset() override in StudentViewSet must ensure
        a student only sees their own profile — not other students.
        This is testing RBAC Layer 1: queryset scoping.
        """
        other_student = User.objects.create_user(
            username='otherstudent',
            email='other@test.com',
            password='pass123',
            role='Student',
            first_name='Other',
            last_name='Student'
        )

        url = reverse('students-list')
        response = student_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_anonymous_user_cannot_see_students(self, api_client):
        """
        Unauthenticated requests to the students list must be denied.
        Your get_queryset() raises PermissionDenied for anonymous users.
        """
        url = reverse('students-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_lecturer_sees_students_in_their_department(
        self, db, lecturer_client, lecturer_user
    ):
        """
        A lecturer's get_queryset() filters students by the lecturer's
        department. This tests that scoping — a lecturer must not see
        students from other departments.
        """
        from academics.models import Department
        from account.models import StudentProfile

        dept = Department.objects.create(
            name='Computer Science',
            description='CS'
        )
        lecturer_user.lecturerprofile.department = dept
        lecturer_user.lecturerprofile.save()

        student_in_dept = User.objects.create_user(
            username='csStudent',
            email='cs@test.com',
            password='pass123',
            role='Student',
            first_name='CS',
            last_name='Student'
        )
        StudentProfile.objects.filter(
            user=student_in_dept
        ).update(department=dept)

        other_dept = Department.objects.create(
            name='Mechanical Engineering',
            description='ME'
        )
        student_other_dept = User.objects.create_user(
            username='meStudent',
            email='me@test.com',
            password='pass123',
            role='Student',
            first_name='ME',
            last_name='Student'
        )
        StudentProfile.objects.filter(
            user=student_other_dept
        ).update(department=other_dept)

        url = reverse('students-list')
        response = lecturer_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1


# ── PERMISSION TESTS ───────────────────────────────────────

class TestProfilePermissions:

    def test_student_cannot_edit_another_students_profile(
        self, db, student_client, student_user
    ):
        """
        IsOwnerOrReadOnly must prevent a student from editing
        another student's profile.
        """
        other_student = User.objects.create_user(
            username='victim',
            email='victim@test.com',
            password='pass123',
            role='Student',
            first_name='Victim',
            last_name='Student'
        )
        other_profile = other_student.studentprofile

        url = reverse('students-detail', kwargs={'pk': other_profile.pk})
        response = student_client.patch(url, {'level': 999})

        assert response.status_code == status.HTTP_404_NOT_FOUND
        
    def test_student_can_read_profiles_in_their_scope(
        self, student_client, student_user
    ):
        """
        SAFE_METHODS (GET) should be allowed by IsOwnerOrReadOnly
        even for profiles that are not your own.
        This tests the ReadOnly part of IsOwnerOrReadOnly.
        """
        url = reverse('students-list')
        response = student_client.get(url)
        assert response.status_code != status.HTTP_403_FORBIDDEN


# ── SERVICE LAYER TESTS ────────────────────────────────────

class TestUserServiceFromAccount:

    def test_new_student_registration_creates_profile(self, db):
        """
        When a brand new student is created, the signal calls
        UserService.create_profile_for_new_user() which must
        create exactly one StudentProfile.
        """
        user = User.objects.create_user(
            username='brandnew',
            email='brandnew@test.com',
            password='pass123',
            role='Student',
            first_name='Brand',
            last_name='New'
        )
        assert StudentProfile.objects.filter(user=user).count() == 1

    def test_role_switch_student_to_lecturer(self, db, student_user):
        """
        Explicitly calling UserService.switch_user_role() must:
        1. Create a LecturerProfile
        2. Soft-delete the StudentProfile (is_active=False)
        """
        from account.services import UserService

        assert StudentProfile.objects.filter(
            user=student_user, is_active=True
        ).exists()

        student_user.role = 'Lecturer'
        student_user.save()
        UserService.switch_user_role(student_user)

        assert LecturerProfile.objects.filter(user=student_user).exists()

        old_profile = StudentProfile.objects.filter(user=student_user).first()
        assert old_profile is not None
        assert old_profile.is_active is False