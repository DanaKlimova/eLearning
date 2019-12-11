from django.urls import path
from accounts import views


urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("registration/", views.registration_view, name="registration"),
    path("account/", views.account_view, name="account"),
    path("logout/", views.logout_view, name="logout"),
]
