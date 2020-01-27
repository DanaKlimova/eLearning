from django.urls import path
from main import views


urlpatterns = [
    path("home/", views.home, name="home"),
    path("current_courses/", views.current_courses, name="current_courses"),
    path("users_courses/", views.users_courses, name="users_courses"),
    path("starred_courses/", views.starred_courses, name="starred_courses"),
]
