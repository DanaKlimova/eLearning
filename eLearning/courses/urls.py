from django.urls import path
from courses import views


urlpatterns = [
    path('', views.CourseListView.as_view(), name="course_list"),
    path('statistics/<int:course_pk>/', views.course_statistics_view, name="course_statistics"),
    path('<int:course_pk>/', views.EditCourseView.as_view(), name="course_edit"),
    path('create/', views.CreateCourseView.as_view(), name="course_create"),
    path('<int:course_pk>/page/<int:page_pk>/', views.EditPageView.as_view(), name="page_edit"),
    path('<int:course_pk>/page/create/', views.CreatePageView.as_view(), name="page_create"),
    path(
        '<int:course_pk>/page/<int:page_pk>/question/<int:question_pk>',
        views.EditQuestionView.as_view(),
        name="question_edit"
    ),
    path(
        '<int:course_pk>/page/<int:page_pk>/question/create/',
        views.CreateQuestionView.as_view(),
        name="question_create"
    ),
    path(
        '<int:course_pk>/page/<int:page_pk>/question/<int:question_pk>/variant/<int:variant_pk>/',
        views.EditVariantView.as_view(),
        name="variant_edit"
    ),
    path(
        '<int:course_pk>/page/<int:page_pk>/question/<int:question_pk>/variant/create/',
        views.CreateVariantView.as_view(),
        name="variant_create"
    ),
    path('learn/<int:course_pk>/', views.CourseDetailView.as_view(), name="course_detail"),
    path('learn/<int:course_pk>/home/welcome/', views.CourseWelcomView.as_view(), name="course_welcom"),
    path('learn/<int:course_pk>/home/page/<int:page_pk>/', views.CoursePageView.as_view(), name="course_page"),
    path('learn/<int:course_pk>/home/rate', views.course_rate, name="course_rate"),
    path('cert/', views.GeneratePDF.as_view()),
]
