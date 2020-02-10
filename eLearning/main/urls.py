from django.urls import path
from main import views


urlpatterns = [
    path("home/", views.home, name="home"),
    path("current_courses/", views.current_courses, name="current_courses"),
    path("users_courses/", views.users_courses, name="users_courses"),
    path("starred_courses/", views.starred_courses, name="starred_courses"),
    path("completed_courses/", views.completed_courses, name="completed_courses"),
    path("recomended_courses/", views.recomended_courses, name="recomended_courses"),
    path('cert/<int:course_pk>/', views.generate_cert, name="course_cert"),
]
