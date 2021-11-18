from rest_framework.permissions import BasePermission


class IsSelf(BasePermission):
    def has_object_permission(self, request, view, user):
        return user == request.user


class IsFollow(BasePermission):
    def has_object_permission(self, request, view, follow):
        return request.user == follow.follower
