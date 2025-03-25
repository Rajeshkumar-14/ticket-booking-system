from django.urls import path

from . import views

app_name = "auth"

urlpatterns = [
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("register/", views.user_registration, name="register"),
    path("reset-password/", views.reset_password, name="reset-password"),
    path("reset-confirm/<uidb64>/<token>/", views.reset_confirm, name="reset-confirm"),
    path("success/", views.success, name="success"),
    path("profile/", views.user_profile, name="profile"),
    path("edit-profile/", views.edit_profile, name="edit-profile"),
    path("complete-profile/", views.complete_profile, name="complete-profile"),
]
