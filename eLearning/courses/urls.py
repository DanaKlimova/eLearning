from django.urls import path
from courses import views


urlpatterns = [
    path('', views.CourseListView.as_view(), name="course_list"),
    path('<int:course_pk>/', views.EditCourseView.as_view(), name="course_edit"),
    path('create/', views.CreateCourseView.as_view(), name="course_create"),
    path('<int:course_pk>/page/<int:page_pk>/', views.EditPageView.as_view(), name="page_edit"),
    path('<int:course_pk>/page/create/', views.CreatePageView.as_view(), name="page_create"),
]
