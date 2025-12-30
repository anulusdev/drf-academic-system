from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    hod = models.OneToOneField(
        'account.LecturerProfile', null=True,
        blank=True, on_delete=models.SET_NULL,
        related_name='managed_department'
    )

    def __str__(self):
        return self.name


class Course(models.Model):
    title = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField()
    unit = models.IntegerField(validators=[MinValueValidator(0)])
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE,
        related_name='courses'
    )
    students = models.ManyToManyField(
        'account.StudentProfile',
        through='Enrollment', blank=True
    )
    lecturer = models.ForeignKey(
        'account.LecturerProfile',
        on_delete=models.SET_NULL, null=True,
        related_name='lectured_courses'
    )

    def __str__(self):
        return self.code


class Enrollment(models.Model):
    # STATUS_CHOICES = (
    #     ('Pending', 'PENDING'),
    #     ('Approved', 'APPROVED'),
    #     ('Rejected', 'REJECTED')
    # )

    student = models.ForeignKey(
        'account.StudentProfile', on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE,
        related_name='enrollments'
    )
    # status = models.CharField(max_length=10, chioces=STATUS_CHOICES, default='Pending')
    # approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    approved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"], name="unique_student_course"
            )
        ]


class AcademicSession(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return f'From {self.start_date} to {self.end_date}'
