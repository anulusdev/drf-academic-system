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
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_staff:
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
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'Student' and
            hasattr(request.user, 'studentprofile')
        )

