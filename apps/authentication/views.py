from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import Group, User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.csrf import ensure_csrf_cookie

from utils.constants import AUTH_ERROR_MESSAGES
from utils.logger import logger

from .decorators import unauthenticated_user
from .forms import LoginForm, ProfileForm, RegistrationForm
from .models import UserProfile
from .tasks import password_change_alert, send_password_reset, send_welcome_email

__project_by__ = "RajeshKumar"


# Helper function to get common context
def get_common_context():
    return {
        "GENDER_CHOICES": UserProfile.GENDER,
        "PAYMENT_METHODS": UserProfile.PAYMENT_METHODS,
    }


@ensure_csrf_cookie
@unauthenticated_user
def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            requested_user = User.objects.filter(username=username).first()

            if requested_user is None:
                logger.warning(f"Login attempt failed: Username '{username}' does not exist.")
                return JsonResponse(
                    {'success': False, 'message': AUTH_ERROR_MESSAGES["USER_NOT_FOUND"]},
                    status=400,
                )

            user = authenticate(request, username=requested_user.username, password=password)
            if user is not None:
                login(request, user)
                redirect_url = "core:index"
                if user.groups.filter(name="Administration").exists():
                    logger.info(f"Admin user '{username}' logged in successfully.")
                    redirect_url = "administration:administration-home"
                elif user.groups.filter(name="User").exists():
                    logger.info(f"User '{username}' logged in successfully.")
                    if not user.userprofile.profile_completed:
                        redirect_url = "auth:complete-profile"
                else:
                    messages.error(request, AUTH_ERROR_MESSAGES["REGISTRATION_REQUIRED"])
                    logger.warning(f"User '{username}' logged in but has no group assigned.")
                    return JsonResponse(
                        {
                            'success': False,
                            'message': AUTH_ERROR_MESSAGES["REGISTRATION_REQUIRED"],
                        },
                        status=400,
                    )

                return JsonResponse(
                    {'success': True, 'message': 'Login successful!', 'redirect_url': redirect_url}
                )
            else:
                logger.warning(
                    f"Login attempt failed for username '{username}': Invalid password."
                )
                return JsonResponse(
                    {'success': False, 'message': AUTH_ERROR_MESSAGES["INVALID_PASSWORD"]},
                    status=400,
                )
        else:
            logger.warning(f"Login form validation failed: {form.errors.as_json()}")
            return JsonResponse(
                {'success': False, 'errors': json.loads(form.errors.as_json())}, status=400
            )

    form = LoginForm()
    context = get_common_context()
    context["form"] = form
    return render(request, "authentication/login.html", context)


def user_logout(request):
    username = request.user.username if request.user.is_authenticated else "Anonymous"
    logout(request)
    logger.info(f"User '{username}' logged out successfully.")
    return redirect("auth:login")


@ensure_csrf_cookie
@unauthenticated_user
def user_registration(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        # Log the submitted form data (excluding password for security)
        form_data = {
            key: value
            for key, value in request.POST.items()
            if key not in ["password", "password1"]
        }
        logger.debug(f"Registration attempt with data: {form_data}")

        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            phone_number = form.cleaned_data["phone_number"]

            try:
                group = Group.objects.get(name="User")
            except Group.DoesNotExist:
                logger.error("User group 'User' does not exist during registration.")
                return JsonResponse(
                    {'success': False, 'message': AUTH_ERROR_MESSAGES["GROUP_NOT_FOUND"]},
                    status=500,
                )

            try:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.groups.add(group)
                user.save()

                user_profile = UserProfile.objects.create(
                    user=user,
                    phone_number=phone_number,
                    profile_completed=False,
                )
                user_profile.save()

                send_welcome_email(email)
                logger.info(f"User '{username}' registered successfully.")
                return JsonResponse(
                    {
                        'success': True,
                        'message': 'Registration successful. Please log in to continue.',
                    }
                )
            except Exception as e:
                logger.error(f"Registration failed for username '{username}': {str(e)}")
                return JsonResponse({'success': False, 'message': str(e)}, status=500)
        else:
            logger.warning(f"Registration form validation failed: {form.errors.as_json()}")
            return JsonResponse(
                {'success': False, 'errors': json.loads(form.errors.as_json())}, status=400
            )

    form = RegistrationForm()
    context = get_common_context()
    context["form"] = form
    return render(request, "authentication/login.html", context)


@unauthenticated_user
def reset_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            send_password_reset(user.pk)
            messages.success(request, "Password reset email sent successfully.")
            logger.info(f"Password reset email sent to '{email}'.")
            return redirect("auth:login")
        except User.DoesNotExist:
            messages.error(request, AUTH_ERROR_MESSAGES["EMAIL_NOT_FOUND"])
            logger.warning(f"Password reset attempt failed: Email '{email}' not found.")

    return render(request, "authentication/reset-email.html")


@unauthenticated_user
def reset_confirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        messages.error(request, AUTH_ERROR_MESSAGES["INVALID_USER"])
        logger.warning(
            f"Password reset attempt failed: Invalid UID '{uidb64}' or token '{token}'."
        )
        return redirect("auth:login")

    if request.method == "POST":
        password = request.POST.get("password")
        password1 = request.POST.get("password1")

        if password == password1:
            form = SetPasswordForm(user, {"new_password1": password, "new_password2": password1})
            if form.is_valid():
                form.save()
                messages.success(
                    request,
                    "Password reset successful. You can now log in with your new password.",
                )
                password_change_alert(user.email)
                logger.info(f"Password reset successful for user '{user.username}'.")
                return redirect("auth:login")
            else:
                messages.error(request, AUTH_ERROR_MESSAGES["INVALID_FORM"])
                logger.warning(f"Password reset form invalid for user '{user.username}'.")
        else:
            messages.error(request, AUTH_ERROR_MESSAGES["PASSWORDS_MISMATCH"])
            logger.warning(
                f"Password reset attempt failed for user '{user.username}': Passwords do not match."
            )
    else:
        form = SetPasswordForm(user)

    context = {"form": form}
    return render(request, "authentication/reset-password.html", context)


@unauthenticated_user
def success(request):
    return render(request, "authentication/success-page.html")


@login_required(login_url="auth:login")
def user_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    context = {"user_profile": user_profile}
    if request.user.groups.filter(name="Administration").exists():
        return render(request, "administration/admin-profile.html", context)
    return render(request, "core/user-profile.html", context)


@login_required(login_url="auth:login")
def complete_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    form = ProfileForm(request.POST or None, instance=user_profile)

    if request.method == "POST" and form.is_valid():
        form.save()
        user_profile.profile_completed = True
        user_profile.save()
        messages.success(request, "Profile completed successfully!")
        logger.info(f"User '{request.user.username}' completed their profile.")
        return redirect("core:index")

    context = get_common_context()
    context["form"] = form
    context["user_profile"] = user_profile
    return render(request, "authentication/complete_profile.html", context)


@login_required(login_url="auth:login")
def edit_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    form = ProfileForm(request.POST or None, instance=user_profile)

    if request.method == "POST" and form.is_valid():
        form.save()
        logger.info(f"User '{request.user.username}' updated their profile.")
        return JsonResponse({"success": True})

    context = get_common_context()
    context["user_profile"] = user_profile
    context["form"] = form

    if request.user.groups.filter(name="Administration").exists():
        return render(request, "administration/admin-profile-edit.html", context)
    return render(request, "core/user-profile-edit.html", context)
