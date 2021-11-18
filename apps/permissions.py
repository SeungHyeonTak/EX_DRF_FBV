from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):

    def has_object_permission(self, request, view, post):  # obj -> post
        return post.user == request.user


class PhotoOwner(BasePermission):

    def has_object_permission(self, request, view, photo):
        return photo.post.user == request.user
