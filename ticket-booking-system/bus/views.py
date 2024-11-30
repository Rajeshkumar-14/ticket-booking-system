from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from core.models import Bus
from django.http import JsonResponse
from .models import BusReservation
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
def bus_home(request):
    bus_types = Bus.BUS_CHOICES
    starting_points = Bus.objects.values_list("start_point", flat=True).distinct()
    ending_points = Bus.objects.values_list("end_point", flat=True).distinct()

    context = {
        "bus_types": bus_types,
        "starting_points": starting_points,
        "ending_points": ending_points,
    }
    return render(request, "bus/bus-home.html", context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["User"])
def check_bus_availability(request):
    start_point = request.POST.get("start_point")
    end_point = request.POST.get("end_point")
    bus_type = request.POST.get("bus_type")
    date = request.POST.get("date")

    try:
        bus = Bus.objects.get(
            start_point=start_point,
            end_point=end_point,
            bus_type=bus_type,
            journey_date=date,
        )
        is_bus_available = True
        bus_details = {
            "bus_id": bus.id,
            "bus_type": bus.bus_type,
            "journey_date": bus.journey_date,
            "start_point": bus.start_point,
            "end_point": bus.end_point,
            "fare": bus.fare,
            "max_seats": bus.max_seats,
        }
    except Bus.DoesNotExist:
        is_bus_available = False
        bus_details = None

    return JsonResponse({"available": is_bus_available, "bus_details": bus_details})


@login_required(login_url="login")
@allowed_users(allowed_roles=["User"])
def bus_reservation(request, id):
    bus = get_object_or_404(Bus, id=id)
    bus_reservations = BusReservation.objects.filter(trip_id=id)
    booked_seat_list = [reservation.seat_numbers for reservation in bus_reservations]
    booked_seat_list_json = json.dumps(booked_seat_list)

    # Calculate the number of remaining seats that can be booked by the user
    user_reservation_count = BusReservation.objects.filter(
        reservation_user=request.user, trip_id=id
    ).count()
    remaining_seats = bus.booking_limit - user_reservation_count

    context = {
        "bus": bus,
        "booked_seat_list_json": booked_seat_list_json,
        "remaining_seats": remaining_seats,
    }

    return render(request, "bus/bus-reservation.html", context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["User"])
@csrf_exempt
def save_bus_reservation(request):
    if request.method == "POST":
        user = request.user

        names = request.POST.getlist("name")
        seat_numbers = request.POST.getlist("seat_number")
        id_proofs = request.FILES.getlist("id_proof")
        trip_id = request.POST.get("trip_id")

        if len(names) != len(seat_numbers) or len(names) != len(id_proofs):
            return JsonResponse(
                {
                    "error": "Invalid data. Names, seat numbers, and id proofs must have the same length."
                },status=400
            )

        user_reservation_count = BusReservation.objects.filter(
            reservation_user=user, trip_id=trip_id
        ).count()
        bus = Bus.objects.get(id=trip_id)
        if user_reservation_count + len(names) > bus.booking_limit:
            return JsonResponse(
                {
                    "error": f"Booking limit exceeded. You can only book {bus.booking_limit - user_reservation_count} more seats."
                },status=400
            )

        for i in range(len(names)):
            name = names[i]
            seat_number = seat_numbers[i]
            id_proof = id_proofs[i]

            # Check for duplicate names and id_proofs
            if BusReservation.objects.filter(
                trip_id=trip_id, passenger_names=name
            ).exists():
                return JsonResponse(
                    {
                        "error": f"Passenger name '{name}' is already booked on this trip."
                    },status=400
                )

            if BusReservation.objects.filter(
                trip_id=trip_id, id_proof=id_proof
            ).exists():
                return JsonResponse(
                    {
                        "error": f"ID proof '{id_proof}' is already used for another reservation on this trip."
                    },status=400
                )

            if BusReservation.objects.filter(
                trip_id=trip_id, seat_numbers=seat_number
            ).exists():
                return JsonResponse({"error": f"Seat {seat_number} is already booked."})

            bus_reservation = BusReservation(
                reservation_user=user,
                trip_id=trip_id,
                seat_numbers=seat_number,
                passenger_names=name,
                id_proof=id_proof,
            )
            bus_reservation.save()

        send_booking_confirmation_email(user.email, user.username, len(names))

        remaining_limit = bus.booking_limit - user_reservation_count - len(names)
        return JsonResponse(
            {"message": "Bus reservations saved successfully.", "remaining_limit": remaining_limit},
            status=200
        )
    return JsonResponse({"error": "Invalid request method."},status=403)


@login_required(login_url="login")
@allowed_users(allowed_roles=["User", "Administration"])
def cancel_bus_reservation(request):
    if request.method == "POST":
        reservation_id = request.POST.get("reservation_id")
        try:
            reservation = BusReservation.objects.get(id=reservation_id)
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
        except BusReservation.DoesNotExist:
            return JsonResponse({"error": "Reservation not found."})
    return JsonResponse({"error": "Invalid request."})


@login_required(login_url="login")
@allowed_users(allowed_roles=["User", "Administration"])
def cancel_bus_trip(request):
    if request.method == "POST":
        trip_name = request.POST.get("trip_name")
        reservation_username = request.POST.get("reservation_user")
        bus_id = request.POST.get("bus_id")
        try:
            bus = Bus.objects.get(bus_name=trip_name, id=bus_id)
            trip_id = bus.id
        except Bus.DoesNotExist:
            return JsonResponse({"error": "Bus not found."})

        try:
            reservation_user = User.objects.get(username=reservation_username)
        except User.DoesNotExist:
            return JsonResponse({"error": "Reservation user not found."})

        reservations_to_cancel = BusReservation.objects.filter(trip_id=trip_id)

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
