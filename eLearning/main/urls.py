from django.urls import path
from main import views


urlpatterns = [
    path("home/", views.home, name="home"),
    path("current_courses/", views.current_courses, name="current_courses"),
]
