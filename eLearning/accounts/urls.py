from django.urls import path
from accounts import views


urlpatterns = [
    path("login/", views.LoginUser.as_view(), name="login"),
    path("registration/", views.RegistrationView.as_view(), name="registration"),
    path("account/", views.account_view, name="account"),
    path("logout/", views.logout_view, name="logout"),
]
