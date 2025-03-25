from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from .decorators import allowed_users
from .models import SupportMessages


def get_admin_user():
    return User.objects.get(username="admin")


@login_required(login_url="auth:login")
@allowed_users(allowed_roles=["User"])
def load_messages(request):
    messages_data = SupportMessages.objects.filter(
        (models.Q(sender=request.user) & models.Q(receiver=get_admin_user()))
        | (models.Q(sender=get_admin_user()) & models.Q(receiver=request.user))
    ).order_by("timestamp")

    messages = []
    for message in messages_data:
        messages.append(
            {
                "content": message.content,
                "sender": message.sender.username,
                "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    return JsonResponse({"messages": messages})


@login_required(login_url="auth:login")
@allowed_users(allowed_roles=["User"])
def support_home(request):
    request.user.last_active = timezone.now()
    request.user.save()

    if request.method == "POST":
        content = request.POST.get("message")
        if content:
            SupportMessages.objects.create(
                sender=request.user,
                receiver=get_admin_user(),
                content=content,
            )
            messages.success(request, "Message sent successfully!")
            return JsonResponse({"status": "success"})

    context = {"user_status": user_status(get_admin_user())}
    return render(request, "support/support-home.html", context)


@login_required(login_url="auth:login")
@allowed_users(allowed_roles=["Administration"])
def load_user_messages(request, user_id):
    try:
        selected_user = User.objects.get(pk=user_id)

        messages = SupportMessages.objects.filter(
            (models.Q(sender=request.user) & models.Q(receiver=selected_user))
            | (models.Q(sender=selected_user) & models.Q(receiver=request.user))
        ).order_by("timestamp")

        serialized_messages = [
            {"sender": message.sender.username, "content": message.content} for message in messages
        ]

        response_data = {
            "messages": serialized_messages,
            "selected_user": selected_user.username,
            "selected_user_id": selected_user.id,
            "user_status": user_status(selected_user),
        }

        return JsonResponse(response_data)

    except User.DoesNotExist:
        return JsonResponse({"error": "Selected user does not exist"}, status=400)


@login_required(login_url="auth:login")
@allowed_users(allowed_roles=["Administration"])
def support_admin(request):
    if request.method == "POST":
        receiver_id = request.POST.get("receiver")
        message_content = request.POST.get("message")

        receiver = User.objects.get(pk=receiver_id)
        SupportMessages.objects.create(
            sender=request.user,
            receiver=receiver,
            content=message_content,
        )

        response_data = {
            "status": "success",
            "user_id": receiver_id,
        }
        return JsonResponse(response_data)

    users = User.objects.exclude(pk=request.user.id)
    selected_user_id = request.GET.get("user_id")
    selected_user = None
    messages = []
    all_messages = []
    for user in users:
        last_message = get_last_message(request.user, user)
        all_messages.append({'user': user, 'last_message': last_message})

    if selected_user_id:
        selected_user = User.objects.get(pk=selected_user_id)
        messages = SupportMessages.objects.filter(
            (models.Q(sender=request.user) & models.Q(receiver=selected_user))
            | (models.Q(sender=selected_user) & models.Q(receiver=request.user))
        ).order_by("timestamp")

    context = {
        "users": users,
        "selected_user": selected_user,
        "messages": messages,
        "all_messages": all_messages,
    }
    return render(request, "support/support-admin.html", context)


def get_last_message(user1, user2):
    return (
        SupportMessages.objects.filter(
            (models.Q(sender=user1) & models.Q(receiver=user2))
            | (models.Q(sender=user2) & models.Q(receiver=user1))
        )
        .order_by("-timestamp")
        .first()
    )


def user_status(user):
    if user.is_authenticated:
        delta = timezone.now() - user.last_login
        if delta.seconds < 10000:
            return "Online"
        else:
            return "Offline"
    else:
        return "Anonymous"


@login_required(login_url="auth:login")
@allowed_users(allowed_roles=["User"])
def clear_conversation(request):
    SupportMessages.objects.filter(sender=request.user).delete()
    SupportMessages.objects.filter(receiver=request.user).delete()
    response_data = {
        "status": "success",
        "user_id": request.user.id,
    }
    return JsonResponse(response_data)


@login_required(login_url="auth:login")
@allowed_users(allowed_roles=["Administration"])
def clear_admin_conversation(request):
    user_id = request.POST.get("user_id")

    SupportMessages.objects.filter(sender=request.user, receiver=user_id).delete()
    SupportMessages.objects.filter(sender=user_id, receiver=request.user).delete()

    response_data = {
        "status": "success",
        "user_id": user_id,
    }
    return JsonResponse(response_data)
