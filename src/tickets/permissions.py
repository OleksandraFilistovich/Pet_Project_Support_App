from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission

from tickets.models import Ticket
from users.constants import Role


class RoleIsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == Role.ADMIN


class RoleIsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == Role.MANAGER


class RoleIsUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == Role.USER


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, instanse: Ticket):
        return request.user == instanse.user


class IsManagerId(BasePermission):
    def has_permission(self, request, view):
        User = get_user_model()
        user = User.objects.get(pk=request.data["manager_id"])
        print(f"===== {user}={user.role}")
        return user.role == Role.MANAGER
