from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.user_view),
    path('me/', views.me_view),
    path('search/', views.user_search),
    path('<int:pk>/', views.user_detail),
    path('token/', views.login),
    path('follow/', views.follows_view),
    path('follow/<int:pk>/', views.follow_view),
]
