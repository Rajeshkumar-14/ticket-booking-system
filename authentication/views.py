from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import Group, User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.http import urlsafe_base64_decode

from .decorators import unauthenticated_user
from .models import UserProfile
from .tasks import password_change_alert, send_password_reset, send_welcome_email

__project_by__ = "RajeshKumar"


@unauthenticated_user
def user_login(request):
    GENDER_CHOICES = UserProfile.GENDER
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        requested_user = User.objects.filter(username=username).first()

        if requested_user is None:
            messages.error(request, "Username does not exist.")
        else:
            user = authenticate(request, username=requested_user.username, password=password)
            if user is not None:
                login(request, user)
                if user.groups.filter(name="Administration").exists():
                    return redirect("administration-home")
                elif user.groups.filter(name="User").exists():
                    return redirect("index")
                else:
                    messages.error(request, "Please Register and Try Again.")
            else:
                messages.error(request, "Invalid Password. Please try again.")
    context = {
        "GENDER_CHOICES": GENDER_CHOICES,
    }
    return render(request, "authentication/login.html", context)


def user_logout(request):
    logout(request)
    return redirect("login")


@unauthenticated_user
def user_registration(request):
    GENDER_CHOICES = UserProfile.GENDER
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password1 = request.POST["password1"]
        age = request.POST["age"]
        gender = request.POST["gender"]
        date_of_birth = request.POST["date_of_birth"]
        aadhaar_number = request.POST["aadhaar_number"]
        phone_number = request.POST["phone_number"]
        id_proof = request.FILES.get("id_proof")

        if password != password1:
            messages.error(request, "Passwords do not match.")
        else:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username is already taken. Please Sign-Up again")
            elif not Group.objects.filter(name="User").exists():
                messages.error(request, "User Group not Created, Try again some other time.")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email is already in use.")
            elif UserProfile.objects.filter(aadhaar_number=aadhaar_number).exists():
                messages.error(request, "Aadhaar Number already exists.")
            elif UserProfile.objects.filter(phone_number=phone_number).exists():
                messages.error(request, "Phone number already registered with another account.")
            elif UserProfile.objects.filter(id_proof=id_proof).exists():
                messages.error(request, "ID Proof has been used for registration before.")
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                selected_group = Group.objects.get(name="User")
                user.groups.add(selected_group)

                user_profile = UserProfile.objects.create(
                    user=user,
                    gender=gender,
                    age=age,
                    date_of_birth=date_of_birth,
                    aadhaar_number=aadhaar_number,
                    phone_number=phone_number,
                    id_proof=id_proof,
                )
                user_profile.save()
                send_welcome_email(email)
                messages.success(request, "Registration successful. You can now log in.")
                return redirect("login")
    context = {
        "GENDER_CHOICES": GENDER_CHOICES,
    }
    return render(request, "authentication/login.html", context)


@unauthenticated_user
def reset_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            send_password_reset(user.pk)
            messages.success(request, "Password reset email sent successfully.")
            return redirect("login")
        except User.DoesNotExist:
            messages.error(request, "User with this email does not exist.")

    return render(request, "authentication/reset-email.html")


@unauthenticated_user
def reset_confirm(request, uidb64, token):
    User = get_user_model()

    # Decode the UID
    uid = urlsafe_base64_decode(uidb64).decode()

    try:
        user = User.objects.get(pk=uid)
    except User.DoesNotExist:
        messages.error(request, "Invalid user. Please try the password reset again.")
        return redirect("login")

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
                return redirect("login")
            else:
                messages.error(
                    request,
                    "Invalid form data. Please correct the errors and try again.",
                )
        else:
            messages.error(request, "Passwords do not match. Please enter matching passwords.")
    else:
        form = SetPasswordForm(user)

    context = {"form": form}
    return render(request, "authentication/reset-password.html", context)


@unauthenticated_user
def success(request):
    return render(request, "authentication/success-page.html")


@login_required(login_url="login")
def user_profile(request):
    if request.method == "GET":
        user_profile = UserProfile.objects.filter(user=request.user)
        context = {"user_profile": user_profile}
        return render(request, "core/user-profile.html", context)


@login_required(login_url="login")
def edit_user_profile(request):
    GENDER_CHOICES = UserProfile.GENDER
    user_profile = UserProfile.objects.get(user=request.user)
    if request.method == "POST":
        user_profile.gender = request.POST.get("gender")
        user_profile.age = request.POST.get("age")
        user_profile.date_of_birth = request.POST.get("date_of_birth")
        user_profile.aadhaar_number = request.POST.get("aadhaar_number")
        user_profile.phone_number = request.POST.get("phone_number")
        user_profile.save()
        return JsonResponse({"success": True})
    context = {
        "user_profile": user_profile,
        "GENDER_CHOICES": GENDER_CHOICES,
    }
    return render(request, "core/user-profile-edit.html", context)


@login_required(login_url="login")
def admin_profile(request):
    if request.method == "GET":
        user_profile = UserProfile.objects.get(user=request.user)
        context = {"user_profile": user_profile}
        return render(request, "administration/admin-profile.html", context)


@login_required(login_url="login")
def edit_admin_profile(request):
    GENDER_CHOICES = UserProfile.GENDER

    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, "Please Complete your profile and try again.")
        return redirect("admin_profile")

    if request.method == "POST":
        user_profile.gender = request.POST.get("gender")
        user_profile.age = request.POST.get("age")
        user_profile.date_of_birth = request.POST.get("date_of_birth")
        user_profile.aadhaar_number = request.POST.get("aadhaar_number")
        user_profile.phone_number = request.POST.get("phone_number")
        user_profile.save()
        return JsonResponse({"success": True})

    context = {
        "user_profile": user_profile,
        "GENDER_CHOICES": GENDER_CHOICES,
    }
    return render(request, "administration/admin-profile-edit.html", context)
