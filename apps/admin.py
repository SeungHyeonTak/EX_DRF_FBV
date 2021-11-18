from django.contrib import admin
from .models import Post, Comment, Photo, Like


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_public', 'created_at', 'updated_at',)
    list_display_links = ('id',)
    search_fields = ('content',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'created_at', 'updated_at',)
    list_display_links = ('id',)
    search_fields = ('content',)


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'created_at', 'updated_at',)
    list_display_links = ('id',)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'created_at',)
    list_display_links = ('id',)
