from django.urls import path
from main import views


urlpatterns = [
    path("home/", views.home, name="home"),
    path("current_courses/", views.current_courses_view, name="current_courses"),
    path("users_courses/", views.users_courses_view, name="users_courses"),
    path("starred_courses/", views.starred_courses_view, name="starred_courses"),
    path("completed_courses/", views.completed_courses_view, name="completed_courses"),
    path("recomended_courses/", views.recommended_courses_view, name="recomended_courses"),
    path('cert/<int:course_pk>/', views.generate_cert_view, name="course_cert"),
]
