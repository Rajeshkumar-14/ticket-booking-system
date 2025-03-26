from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import Group, User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.http import urlsafe_base64_decode

from .decorators import unauthenticated_user
from .forms import LoginForm, ResetPasswordRequestForm, UserProfileForm, UserRegistrationForm
from .models import UserProfile
from .tasks import password_change_alert, send_password_reset, send_welcome_email

__project_by__ = "RajeshKumar"


def _get_gender_choices_context():
    """Helper to provide GENDER_CHOICES to templates."""
    return {"GENDER_CHOICES": UserProfile.GENDER_CHOICES}


@unauthenticated_user
def user_login(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "Invalid username or password.")
        else:
            login(request, user)
            if user.groups.filter(name="Administration").exists():
                return redirect("administration:administration-home")
            elif user.groups.filter(name="User").exists():
                return redirect("core:index")
            else:
                messages.error(request, "User not assigned to any group. Please register again.")
                return redirect("authentication:login")
    return render(request, "authentication/login.html", {"form": form, **_get_gender_choices_context()})


def user_logout(request):
    logout(request)
    return redirect("authentication:login")


@unauthenticated_user
def user_registration(request):
    user_form = UserRegistrationForm(request.POST or None)
    profile_form = UserProfileForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and user_form.is_valid() and profile_form.is_valid():
        user = user_form.save()
        user_group, _ = Group.objects.get_or_create(name="User")
        user.groups.add(user_group)

        profile = profile_form.save(commit=False)
        profile.user = user
        profile.save()

        send_welcome_email.delay(user.email)
        messages.success(request, "Registration successful. You can now log in.")
        return redirect("authentication:login")

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        **_get_gender_choices_context(),
    }
    return render(request, "authentication/login.html", context)


@unauthenticated_user
def reset_password(request):
    form = ResetPasswordRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = User.objects.get(email=form.cleaned_data["email"])
        send_password_reset.delay(user.pk)
        messages.success(request, "Password reset email sent successfully.")
        return redirect("authentication:login")
    return render(request, "authentication/reset-email.html", {"form": form})


@unauthenticated_user
def reset_confirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError):
        messages.error(request, "Invalid reset link. Please try again.")
        return redirect("authentication:login")

    form = SetPasswordForm(user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        password_change_alert.delay(user.email)
        messages.success(request, "Password reset successful. You can now log in.")
        return redirect("authentication:login")

    return render(request, "authentication/reset-password.html", {"form": form})


@unauthenticated_user
def success(request):
    return render(request, "authentication/success-page.html")


@login_required(login_url="authentication:login")
def user_profile(request):
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        messages.error(request, "Please complete your profile.")
        return redirect("authentication:edit_user_profile")
    return render(request, "core/user-profile.html", {"user_profile": user_profile})


@login_required(login_url="authentication:login")
def edit_profile(request, template_name, redirect_name):
    """Generic view to edit user or admin profile."""
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile(user=request.user)

    form = UserProfileForm(request.POST or None, request.FILES or None, instance=user_profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        return JsonResponse({"success": True})

    return render(request, template_name, {"form": form, **_get_gender_choices_context()})


@login_required(login_url="authentication:login")
def user_profile_edit(request):
    return edit_profile(request, "core/user-profile-edit.html", "authentication:user_profile")

@login_required(login_url="authentication:login")
def admin_profile(request):
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        messages.error(request, "Please complete your profile.")
        return redirect("authentication:edit_admin_profile")
    return render(request, "administration/admin-profile.html", {"user_profile": user_profile})


@login_required(login_url="authentication:login")
def admin_profile_edit(request):
    return edit_profile(request, "administration/admin-profile-edit.html", "authentication:admin_profile")
