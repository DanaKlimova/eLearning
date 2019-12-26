from django.urls import path
from courses import views


urlpatterns = [
    path('', views.CourseListView.as_view(), name="course_list"),
    path('<int:pk>/', views.CourseDetailView.as_view(), name="course_detail"),
]
