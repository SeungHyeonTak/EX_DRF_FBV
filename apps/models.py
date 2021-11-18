import os
from uuid import uuid4
from django.utils import timezone
from django.db import models


def get_photo_path(instance, filename):
    url = 'photo_image'
    ymd_path = timezone.now().strftime('%Y/%m/%d')
    uuid_name = uuid4().hex
    extension = os.path.splitext(filename)[-1].lower()

    return '/'.join([url, ymd_path, uuid_name + extension])


class Post(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(blank=True)

    lat = models.DecimalField(max_digits=10, decimal_places=6, blank=True)
    lng = models.DecimalField(max_digits=10, decimal_places=6, blank=True)

    is_public = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']


class Comment(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']


class Photo(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image = models.ImageField(verbose_name='image', upload_to=get_photo_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']


class Like(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='like_user')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='like_post')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
