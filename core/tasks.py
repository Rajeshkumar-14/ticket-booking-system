from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from celery import shared_task

__project_by__ = "RajeshKumar"

def send_booking_confirmation_email(user_email, user_name, ticket_count):
    subject = "BOOKING CONFIRMED"
    html_message = render_to_string(
        "email/booking-confirmation-mail.html",
        {"user_name": user_name, "ticket_count": ticket_count},
    )
    plain_message = strip_tags(html_message)
    from_email = "noreply@example.com"
    recipient_list = [user_email]

    send_mail(
        subject, plain_message, from_email, recipient_list, html_message=html_message
    )
    print("Booking COnfirm mail sent")


def send_booking_cancellation_email(user_email, user_name):
    subject = "BOOKING CANCELLED"
    html_message = render_to_string(
        "email/booking-cancel-mail.html", {"user_name": user_name}
    )
    plain_message = strip_tags(html_message)
    from_email = "noreply@example.com"
    recipient_list = [user_email]

    send_mail(
        subject, plain_message, from_email, recipient_list, html_message=html_message
    )
    print("CANCEL EMAIL SENT")


def send_booking_cancellation_email_by_admin(user_email, user_name):
    subject = "BOOKING CANCELLED by ADMIN"
    html_message = render_to_string(
        "email/booking-cancel-admin-mail.html", {"user_name": user_name}
    )
    plain_message = strip_tags(html_message)
    from_email = "noreply@example.com"
    recipient_list = [user_email]

    send_mail(
        subject, plain_message, from_email, recipient_list, html_message=html_message
    )
    print("CANCEL EMAIL BY ADMIN SENT")
