import pytest
from django.urls import reverse
from rest_framework import status
from academics.models import Course, Department, Enrollment
from account.models import LecturerProfile, StudentProfile


# ── SETUP HELPERS ──────────────────────────────────────────

@pytest.fixture
def department(db):
    return Department.objects.create(
        name='Computer Science',
        description='CS Department'
    )


@pytest.fixture
def other_department(db):
    return Department.objects.create(
        name='Mechanical Engineering',
        description='ME Department'
    )


@pytest.fixture
def lecturer_with_department(lecturer_user, department):
    profile = lecturer_user.lecturerprofile
    profile.department = department
    profile.save()
    return lecturer_user


@pytest.fixture
def hod_user(lecturer_with_department, department):
    """Makes the lecturer the HOD of the department."""
    profile = lecturer_with_department.lecturerprofile
    department.hod = profile
    department.save()
    return lecturer_with_department


@pytest.fixture
def student_with_department(student_user, department):
    profile = student_user.studentprofile
    profile.department = department
    profile.save()
    return student_user


@pytest.fixture
def course(department, lecturer_with_department):
    return Course.objects.create(
        title='Introduction to Programming',
        code='CSC101',
        description='Intro course',
        unit=3,
        department=department,
        lecturer=lecturer_with_department.lecturerprofile
    )


# ── RBAC TESTS ─────────────────────────────────────────────

class TestCoursePermissions:

    def test_unauthenticated_user_can_list_courses(self, api_client, course):
        """Anyone can browse courses — this is intentional."""
        url = reverse('courses-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_student_cannot_create_course(self, student_client, department):
        """Students must not be able to create courses."""
        url = reverse('courses-list')
        data = {
            'title': 'Hacked Course',
            'code': 'HACK101',
            'description': 'Should not be created',
            'unit': 3,
            'department': department.id
        }
        response = student_client.post(url, data)
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_401_UNAUTHORIZED
        ]

    def test_admin_can_create_course(self, admin_client, department):
        """Admins must be able to create courses."""
        url = reverse('courses-list')
        data = {
            'title': 'New Course',
            'code': 'NEW101',
            'description': 'Admin created',
            'unit': 3,
            'department': department.id
        }
        response = admin_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED


# ── ENROLLMENT TESTS ───────────────────────────────────────

class TestEnrollmentLogic:

    def test_student_can_enroll_in_department_course(
        self, student_client, student_with_department, course
    ):
        """A student should be able to enroll in a course from their department."""
        url = reverse('courses-enroll', kwargs={'pk': course.pk})
        response = student_client.post(url)
        assert response.status_code == status.HTTP_201_CREATED
        assert Enrollment.objects.filter(
            student=student_with_department.studentprofile,
            course=course
        ).exists()

    def test_duplicate_enrollment_is_rejected(
        self, student_client, student_with_department, course
    ):
        """Enrolling twice in the same course must return 400."""
        Enrollment.objects.create(
            student=student_with_department.studentprofile,
            course=course
        )
        url = reverse('courses-enroll', kwargs={'pk': course.pk})
        response = student_client.post(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_student_cannot_enroll_outside_department(
        self, student_client, student_with_department,
        other_department, db
    ):
        """A student must not enroll in courses outside their department."""
        other_course = Course.objects.create(
            title='Foreign Course',
            code='FOR101',
            description='Not your department',
            unit=2,
            department=other_department
        )
        url = reverse('courses-enroll', kwargs={'pk': other_course.pk})
        response = student_client.post(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_lecturer_cannot_enroll_in_course(
        self, lecturer_client, course
    ):
        """Lecturers are not students — enrollment must be denied."""
        url = reverse('courses-enroll', kwargs={'pk': course.pk})
        response = lecturer_client.post(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ── SERVICE LAYER TESTS ────────────────────────────────────

class TestUserService:

    def test_role_switch_creates_new_profile(self, db, student_user):
        """Switching from Student to Lecturer must create a LecturerProfile."""
        from account.services import UserService
        student_user.role = 'Lecturer'
        student_user.save()
        UserService.switch_user_role(student_user)
        assert LecturerProfile.objects.filter(user=student_user).exists()

    def test_role_switch_deactivates_old_profile(self, db, student_user):
        """The old StudentProfile must be soft-deleted on role switch."""
        from account.services import UserService
        student_user.role = 'Lecturer'
        student_user.save()
        UserService.switch_user_role(student_user)
        old_profile = StudentProfile.objects.filter(user=student_user).first()
        if old_profile:
            assert old_profile.is_active is False