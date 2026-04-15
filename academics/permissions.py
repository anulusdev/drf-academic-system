from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
                request.method in permissions.SAFE_METHODS or
                request.user and
                request.user.is_staff
                )

    # def has_object_permission(self, request, view, obj):
    #     if request.method in permissions.SAFE_METHODS:
    #         return True
    #     if request.user.is_staff:
    #         return True
    #     if obj.lecturer is None:
    #         return False
    #     return obj.lecturer.user == request.user


class IsHodOrReadOnly(permissions.BasePermission):
    """
    View-level: allows authenticated lecturers through for write attempts.
    Object-level: only the HOD of the relevant department can mutate.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS or request.user.is_staff:
            return True
        
        if hasattr(obj, 'hod'):
            return obj.hod is not None and obj.hod.user == request.user

        elif hasattr(obj, 'department'):
            department = obj.department
            return department is not None and \
                   department.hod is not None and \
                   department.hod.user == request.user

        return False


class IsStudent(permissions.BasePermission):
    """
    Grants access only to authenticated users with a StudentProfile.
    """
    message = 'Only users with a Student profile can perform this action.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.is_student and
            hasattr(request.user, 'studentprofile')
        )

class IsLecturer(permissions.BasePermission):
    """
    Grants access only to authenticated users with a LecturerProfile.
    """
    message = 'Only users with a Lecturer profile can perform this action.'
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.is_lecturer and
            hasattr(request.user, 'lecturerprofile')
        )

