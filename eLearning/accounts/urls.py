from django.urls import path
from accounts import views


urlpatterns = [
    path("login/", views.LoginUser.as_view(), name="login"),
    path("registration/", views.RegistrationView.as_view(), name="registration"),
    path("account/", views.AccountView.as_view(), name="account"),
    path("logout/", views.LogoutUser.as_view(), name="logout"),
    path('organizations', views.OrganizationListView.as_view(), name="organization_list"),
]
