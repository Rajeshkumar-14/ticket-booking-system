from django.urls import path

from . import views

__project_by__ = "RajeshKumar"

urlpatterns = [
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("registration/", views.user_registration, name="register"),
    path("reset-password/", views.reset_password, name="reset-password"),
    path(
        "password_reset_confirm/<uidb64>/<token>/",
        views.reset_confirm,
        name="passwordresetconfirm",
    ),
    path("success/", views.success, name="success"),
    path("user-profile/", views.user_profile, name="user_profile"),
    path("edit-profile/", views.edit_user_profile, name="edit_user_profile"),
    path("admin-profile/", views.admin_profile, name="admin_profile"),
    path("edit-admin-profile/", views.edit_admin_profile, name="edit_admin_profile"),
]
