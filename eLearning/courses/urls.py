from django.urls import path
from courses import views


urlpatterns = [
    path('', views.CourseListView.as_view(), name="course_list"),
    path('<int:pk>/', views.EditCourseView.as_view(), name="course_edit"),
    path('create/', views.CreateCourseView.as_view(), name="course_create"),
]
