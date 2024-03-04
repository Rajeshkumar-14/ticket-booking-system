from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from core.models import Train
from django.http import JsonResponse
from .models import TrainReservation
from django.views.decorators.csrf import csrf_exempt
import json

from .decorators import allowed_users
from django.contrib.auth.decorators import login_required

from core.tasks import (
    send_booking_confirmation_email,
    send_booking_cancellation_email,
    send_booking_cancellation_email_by_admin,
)

__project_by__ = "RajeshKumar"


@login_required(login_url="login")
@allowed_users(allowed_roles=["User"])
def train_home(request):
    train_types = Train.TRAIN_CHOICES
    starting_points = Train.objects.values_list(
        "departure_station", flat=True
    ).distinct()
    ending_points = Train.objects.values_list("arrival_station", flat=True).distinct()

    context = {
        "train_types": train_types,
        "starting_points": starting_points,
        "ending_points": ending_points,
    }
    return render(request, "train/train-home.html", context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["User"])
def check_train_availability(request):
    start_point = request.POST.get("start_point")
    end_point = request.POST.get("end_point")
    train_type = request.POST.get("train_type")
    date = request.POST.get("date")

    try:
        train = Train.objects.get(
            departure_station=start_point,
            arrival_station=end_point,
            train_type=train_type,
            departure_date=date,
        )
        is_train_available = True
        train_details = {
            "train_id": train.id,
            "train_type": train.train_type,
            "departure_date": train.departure_date,
            "departure_station": train.departure_station,
            "arrival_station": train.arrival_station,
            "fare": train.fare,
            "max_seats": train.max_seats,
        }
    except Train.DoesNotExist:
        is_train_available = False
        train_details = None

    return JsonResponse(
        {"available": is_train_available, "train_details": train_details}
    )


@login_required(login_url="login")
@allowed_users(allowed_roles=["User"])
def train_reservation(request, id):
    train = get_object_or_404(Train, id=id)
    train_reservations = TrainReservation.objects.filter(trip_id=id)
    booked_seat_list = [reservation.seat_numbers for reservation in train_reservations]
    booked_seat_list_json = json.dumps(booked_seat_list)
    # Calculate the number of remaining seats that can be booked by the user
    user_reservation_count = TrainReservation.objects.filter(
        reservation_user=request.user, trip_id=id
    ).count()
    remaining_seats = train.booking_limit - user_reservation_count
    context = {
        "train": train,
        "booked_seat_list_json": booked_seat_list_json,
        "remaining_seats": remaining_seats,
    }
    return render(request, "train/train-reservation.html", context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["User"])
@csrf_exempt
def save_train_reservation(request):
    if request.method == "POST":
        user = request.user

        names = request.POST.getlist("name")
        seat_numbers = request.POST.getlist("seat_number")
        id_proofs = request.FILES.getlist("id_proof")
        trip_id = request.POST.get("trip_id")

        if len(names) != len(seat_numbers) or len(names) != len(id_proofs):
            return JsonResponse(
                {
                    "error": "Invalid data. Names, seat numbers, and ID proofs must have the same length."
                },
                status=400,
            )

        user_reservation_count = TrainReservation.objects.filter(
            reservation_user=user, trip_id=trip_id
        ).count()
        train = Train.objects.get(id=trip_id)
        if user_reservation_count + len(names) > train.booking_limit:
            return JsonResponse(
                {
                    "error": f"Booking limit exceeded. You can only book {train.booking_limit - user_reservation_count} more seats."
                },
                status=400,
            )

        for i in range(len(names)):
            name = names[i]
            seat_number = seat_numbers[i]
            id_proof = id_proofs[i]

            # Check for duplicate names and ID proofs
            if TrainReservation.objects.filter(
                trip_id=trip_id, passenger_names=name
            ).exists():
                return JsonResponse(
                    {
                        "error": f"Passenger name '{name}' is already booked on this trip."
                    },
                    status=400,
                )

            if TrainReservation.objects.filter(
                trip_id=trip_id, id_proof=id_proof
            ).exists():
                return JsonResponse(
                    {
                        "error": f"ID proof '{id_proof}' is already used for another reservation on this trip."
                    },
                    status=400,
                )

            if TrainReservation.objects.filter(
                trip_id=trip_id, seat_numbers=seat_number
            ).exists():
                return JsonResponse({"error": f"Seat {seat_number} is already booked."})

            train_reservation = TrainReservation(
                reservation_user=user,
                trip_id=trip_id,
                seat_numbers=seat_number,
                passenger_names=name,
                id_proof=id_proof,
            )
            train_reservation.save()

        send_booking_confirmation_email(user.email, user.username, len(names))

        remaining_limit = train.booking_limit - user_reservation_count - len(names)
        return JsonResponse(
            {
                "message": "Bus reservations saved successfully.",
                "remaining_limit": remaining_limit,
            },
            status=200,
        )

    return JsonResponse({"error": "Invalid request method."}, status=405)


@login_required(login_url="login")
@allowed_users(allowed_roles=["User", "Administration"])
def cancel_train_reservation(request):
    if request.method == "POST":
        reservation_id = request.POST.get("reservation_id")
        try:
            reservation = TrainReservation.objects.get(id=reservation_id)
            reservation.delete()
            if request.user == reservation.reservation_user:
                send_booking_cancellation_email(
                    reservation.reservation_user.email, reservation.reservation_user
                )
            else:
                send_booking_cancellation_email_by_admin(
                    reservation.reservation_user.email, reservation.reservation_user
                )
            return JsonResponse({"success": "Reservation has been cancelled."})
        except TrainReservation.DoesNotExist:
            return JsonResponse({"error": "Reservation not found."})

    return JsonResponse({"error": "Invalid request."})


@login_required(login_url="login")
@allowed_users(allowed_roles=["User", "Administration"])
def cancel_train_trip(request):
    if request.method == "POST":
        trip_name = request.POST.get("trip_name")
        reservation_username = request.POST.get("reservation_user")
        train_id = request.POST.get("train_id")
        try:
            train = Train.objects.get(train_name=trip_name, id=train_id)
            trip_id = train.id
        except Train.DoesNotExist:
            return JsonResponse({"error": "Train not found."})

        try:
            reservation_user = User.objects.get(username=reservation_username)
        except User.DoesNotExist:
            return JsonResponse({"error": "Reservation user not found."})

        reservations_to_cancel = TrainReservation.objects.filter(trip_id=trip_id)

        if request.user == reservation_user:
            reservations_to_cancel = reservations_to_cancel.filter(
                reservation_user=reservation_user
            )
        elif request.user.is_staff:
            pass
        else:
            return JsonResponse({"error": "Unauthorized access."})

        if reservations_to_cancel.exists():
            reservations_to_cancel.delete()
            return JsonResponse(
                {"success": "Reservations for this trip have been cancelled."}
            )
        else:
            return JsonResponse(
                {
                    "error": "No reservations found for this trip under the provided user account."
                }
            )
    return JsonResponse({"error": "Invalid request."})
