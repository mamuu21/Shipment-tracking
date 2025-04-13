from rest_framework.permissions import BasePermission

class RolePermission(BasePermission):
    allowed_roles = []

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in self.allowed_roles
        )

class IsAdmin(RolePermission):
    allowed_roles = ['admin']

class IsStaff(RolePermission):
    allowed_roles = ['staff']

class IsCustomer(RolePermission):
    allowed_roles = ['customer']

class IsAdminOrStaff(RolePermission):
    allowed_roles = ['admin', 'staff']

class IsAdminOrStaffOrCustomer(RolePermission):
    allowed_roles = ['admin', 'staff', 'customer']
