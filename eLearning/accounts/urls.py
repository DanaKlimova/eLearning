from django.urls import path
from accounts import views


urlpatterns = [
    path("login/", views.LoginUser.as_view(), name="login"),
    path("registration/", views.RegistrationView.as_view(), name="registration"),
    path("account/", views.AccountView.as_view(), name="account"),
    path("logout/", views.LogoutUser.as_view(), name="logout"),
    path('organizations/', views.OrganizationListView.as_view(), name="organization_list"),
    path('manage_organizations/', views.ManageOrganizationListView.as_view(), name="organization_manage_list"),
    path('organizations/sign_as/<int:organization_pk>', views.sign_as, name="organization_sign_as"),
    path('organizations/unsign_as/<int:organization_pk>', views.unsign_as, name="organization_unsign_as"),
    path('organizations/', views.OrganizationListView.as_view(), name="organization_list"),
    path('organizations/add_employee/<int:organization_pk>', views.add_employee, name="add_employee"),
    path('organizations/create', views.CreateOrganizationView.as_view(), name="organization_create"),
    path('organizations/edit/<int:organization_pk>', views.EditOrganizationView.as_view(), name="organization_edit"),
]
