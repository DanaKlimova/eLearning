from django.urls import path
from accounts import views


urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("registration/", views.registration_view, name="registration"),
]
