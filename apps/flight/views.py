import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt

from apps.core.models import Flight
from apps.core.tasks import (
    send_booking_cancellation_email,
    send_booking_cancellation_email_by_admin,
    send_booking_confirmation_email,
)

from .decorators import allowed_users
from .models import FlightReservation

__project_by__ = "RajeshKumar"


@login_required(login_url="auth:login")
@allowed_users(allowed_roles=["User"])
def flight_home(request):
    flight_types = Flight.FLIGHT_CHOICES
    departure_airports = Flight.objects.values_list("departure_airport", flat=True).distinct()
    destination_airports = Flight.objects.values_list("arrival_airport", flat=True).distinct()

    context = {
        "flight_types": flight_types,
        "departure_airports": departure_airports,
        "destination_airports": destination_airports,
    }
    return render(request, "flight/flight-home.html", context)


@login_required(login_url="auth:login")
@allowed_users(allowed_roles=["User"])
def check_flight_availability(request):
    departure = request.POST.get("departure")
    destination = request.POST.get("destination")
    flight_type = request.POST.get("flight_type")
    date = request.POST.get("date")

    try:
        flight = Flight.objects.get(
            departure_airport=departure,
            arrival_airport=destination,
            flight_type=flight_type,
            departure_date=date,
        )
        is_flight_available = True
        flight_details = {
            "flight_id": flight.id,
            "flight_type": flight.flight_type,
            "journey_date": flight.departure_date,
            "departure_airport": flight.departure_airport,
            "destination_airport": flight.arrival_airport,
            "fare": flight.fare,
            "max_seats": flight.max_seats,
        }
    except Flight.DoesNotExist:
        is_flight_available = False
        flight_details = None

    return JsonResponse({"available": is_flight_available, "flight_details": flight_details})


@login_required(login_url="auth:login")
@allowed_users(allowed_roles=["User"])
def flight_reservation(request, id):
    flight = get_object_or_404(Flight, id=id)
    flight_reservations = FlightReservation.objects.filter(trip_id=id)
    booked_seat_list = [reservation.seat_numbers for reservation in flight_reservations]
    booked_seat_list_json = json.dumps(booked_seat_list)
    # Calculate the number of remaining seats that can be booked by the user
    user_reservation_count = FlightReservation.objects.filter(
        reservation_user=request.user, trip_id=id
    ).count()
    remaining_seats = flight.booking_limit - user_reservation_count
    context = {
        "flight": flight,
        "booked_seat_list_json": booked_seat_list_json,
        "remaining_seats": remaining_seats,
    }
    return render(request, "flight/flight-reservation.html", context)


@login_required(login_url="auth:login")
@allowed_users(allowed_roles=["User"])
@csrf_exempt
def save_flight_reservation(request):
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
                },
                status=400,
            )

        user_reservation_count = FlightReservation.objects.filter(
            reservation_user=user, trip_id=trip_id
        ).count()
        flight = Flight.objects.get(id=trip_id)
        if user_reservation_count + len(names) > flight.booking_limit:
            return JsonResponse(
                {
                    "error": f"Booking limit exceeded. You can only book {flight.booking_limit - user_reservation_count} more seats."
                },
                status=400,
            )

        for i in range(len(names)):
            name = names[i]
            seat_number = seat_numbers[i]
            id_proof = id_proofs[i]

            # Check for duplicate names and id_proofs
            if FlightReservation.objects.filter(trip_id=trip_id, passenger_names=name).exists():
                return JsonResponse(
                    {"error": f"Passenger name '{name}' is already booked on this trip."},
                    status=400,
                )

            if FlightReservation.objects.filter(trip_id=trip_id, id_proof=id_proof).exists():
                return JsonResponse(
                    {
                        "error": f"ID proof '{id_proof}' is already used for another reservation on this trip."
                    },
                    status=400,
                )

            if FlightReservation.objects.filter(
                trip_id=trip_id, seat_numbers=seat_number
            ).exists():
                return JsonResponse(
                    {"error": f"Seat {seat_number} is already booked."}, status=400
                )

            flight_reservation = FlightReservation(
                reservation_user=user,
                trip_id=trip_id,
                seat_numbers=seat_number,
                passenger_names=name,
                id_proof=id_proof,
            )
            flight_reservation.save()

        send_booking_confirmation_email(user.email, user.username, len(names))
        remaining_limit = flight.booking_limit - user_reservation_count - len(names)
        return JsonResponse(
            {
                "message": "Fight reservations saved successfully.",
                "remaining_limit": remaining_limit,
            },
            status=201,
        )

    return JsonResponse({"error": "Invalid request method."}, status=405)


@login_required(login_url="auth:login")
@allowed_users(allowed_roles=["User", "Administration"])
def cancel_flight_reservation(request):
    if request.method == "POST":
        reservation_id = request.POST.get("reservation_id")
        try:
            reservation = FlightReservation.objects.get(id=reservation_id)
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
        except FlightReservation.DoesNotExist:
            return JsonResponse({"error": "Reservation not found."})

    return JsonResponse({"error": "Invalid request."})


@login_required(login_url="auth:login")
@allowed_users(allowed_roles=["User", "Administration"])
def cancel_flight_trip(request):
    if request.method == "POST":
        trip_name = request.POST.get("trip_name")
        reservation_username = request.POST.get("reservation_user")
        flight_id = request.POST.get("flight_id")
        try:
            flight = Flight.objects.get(flight_name=trip_name, id=flight_id)
            trip_id = flight.id
        except Flight.DoesNotExist:
            return JsonResponse({"error": "Flight not found."})

        try:
            reservation_user = User.objects.get(username=reservation_username)
        except User.DoesNotExist:
            return JsonResponse({"error": "Reservation user not found."})

        reservations_to_cancel = FlightReservation.objects.filter(trip_id=trip_id)

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
            return JsonResponse({"success": "Reservations for this trip have been cancelled."})
        else:
            return JsonResponse(
                {"error": "No reservations found for this trip under the provided user account."}
            )
    return JsonResponse({"error": "Invalid request."})
