from django.urls import path
from . import views

app_name = 'apps'

urlpatterns = [
    # 후행 슬래시 주의
    path('post/', views.posts_view),
    path('post/search/', views.post_search),
    path('post/<int:pk>/', views.post_view),
    path('post/favs/', views.posts_fav),
    path('post/favs/<int:pk>/', views.post_fav),
    path('comment/', views.comments_view),
    path('comment/<int:pk>/', views.comment_view),
    path('photo/', views.photos_view),
    path('photo/<int:pk>', views.photo_view),
]
