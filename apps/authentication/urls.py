from django.urls import path

from . import views

app_name = "auth"

__project_by__ = "RajeshKumar"

urlpatterns = [
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("register/", views.user_registration, name="register"),
    path("reset-password/", views.reset_password, name="reset-password"),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        views.reset_confirm,
        name="password_reset_confirm",
    ),
    path("success/", views.success, name="success"),
    path("profile/", views.user_profile, name="user_profile"),
    path("profile/edit/", views.user_profile_edit, name="edit_user_profile"),
    path("admin-profile/", views.admin_profile, name="admin_profile"),
    path("admin-profile/edit/", views.admin_profile_edit, name="edit_admin_profile"),
]