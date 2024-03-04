from django.shortcuts import render, get_object_or_404
from .models import Bus, Flight, Train
from bus.models import BusReservation
from flight.models import FlightReservation
from train.models import TrainReservation
from django.http import JsonResponse

from .decorators import allowed_users
from django.contrib.auth.decorators import login_required

__project_by__ = "RajeshKumar"


@login_required(login_url="login")
@allowed_users(allowed_roles=["User"])
def index(request):
    return render(request, "core/index.html")


@login_required(login_url="login")
@allowed_users(allowed_roles=["User"])
def bus_booking_history(request):
    user = request.user
    history = BusReservation.objects.filter(reservation_user=user, status="Booked")
    bus_info = []
    for reservation in history:
        trip_id = reservation.trip_id
        try:
            bus = Bus.objects.get(pk=trip_id)
            bus_info.append(bus)
        except Bus.DoesNotExist:
            bus_info.append(None)

    grouped_data = {}
    for reservation, bus in zip(history, bus_info):
        if bus:
            key = (bus.bus_name, bus.bus_type, bus.journey_date, bus.fare, bus.id)
            if key not in grouped_data:
                grouped_data[key] = []
            grouped_data[key].append((reservation, bus))
    context = {"grouped_data": grouped_data}
    print(grouped_data)
    return render(
        request, "history/user/booking-history/bus-booking-history.html", context
    )


@login_required(login_url="login")
@allowed_users(allowed_roles=["User"])
def bus_travel_history(request):
    user = request.user
    history = BusReservation.objects.filter(reservation_user=user, status="Completed")
    bus_info = []
    for reservation in history:
        trip_id = reservation.trip_id
        try:
            bus = Bus.objects.get(pk=trip_id)
            bus_info.append(bus)
        except Bus.DoesNotExist:
            bus_info.append(None)

    grouped_data = {}
    for reservation, bus in zip(history, bus_info):
        if bus:
            key = (bus.bus_name, bus.bus_type, bus.journey_date, bus.fare)
            if key not in grouped_data:
                grouped_data[key] = []
            grouped_data[key].append((reservation, bus))
    context = {"grouped_data": grouped_data}
    return render(
        request, "history/user/travel-history/bus-travel-history.html", context
    )


def bus_reservation_details(request):
    trip_name = request.POST.get("trip_name")
    user = request.user
    bus = get_object_or_404(Bus, bus_name=trip_name)
    reservations = BusReservation.objects.filter(
        trip_id=bus.id, reservation_user=user, status="Booked"
    )

    reservation_data = []
    for reservation in reservations:
        reservation_data.append(
            {
                "reservation_user": reservation.reservation_user.username,
                "passenger_names": reservation.passenger_names,
                "seat_numbers": reservation.seat_numbers,
                "status": reservation.status,
                "created_at": reservation.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    bus_data = {
        "bus_name": bus.bus_name,
        "bus_type": bus.bus_type,
        "journey_date": bus.journey_date.strftime("%Y-%m-%d"),
        "start_point": bus.start_point,
        "end_point": bus.end_point,
        "fare": str(bus.fare),
        "max_seats": str(bus.max_seats),
    }

    response_data = {
        "bus_data": bus_data,
        "reservation_data": reservation_data,
    }

    return JsonResponse(response_data)


def bus_reservation_history_details(request):
    trip_name = request.POST.get("trip_name")
    user = request.user
    bus = get_object_or_404(Bus, bus_name=trip_name)
    reservations = BusReservation.objects.filter(
        trip_id=bus.id, reservation_user=user, status="Completed"
    )

    reservation_data = []
    for reservation in reservations:
        reservation_data.append(
            {
                "reservation_user": reservation.reservation_user.username,
                "passenger_names": reservation.passenger_names,
                "seat_numbers": reservation.seat_numbers,
                "status": reservation.status,
                "created_at": reservation.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    bus_data = {
        "bus_name": bus.bus_name,
        "bus_type": bus.bus_type,
        "journey_date": bus.journey_date.strftime("%Y-%m-%d"),
        "start_point": bus.start_point,
        "end_point": bus.end_point,
        "fare": str(bus.fare),
        "max_seats": str(bus.max_seats),
    }

    response_data = {
        "bus_data": bus_data,
        "reservation_data": reservation_data,
    }

    return JsonResponse(response_data)


@login_required(login_url="login")
@allowed_users(allowed_roles=["User"])
def flight_booking_history(request):
    user = request.user
    history = FlightReservation.objects.filter(reservation_user=user, status="Booked")
    flight_info = []

    for reservation in history:
        trip_id = reservation.trip_id
        try:
            flight = Flight.objects.get(pk=trip_id)
            flight_info.append(flight)
        except Flight.DoesNotExist:
            flight_info.append(None)

    grouped_data = {}
    for reservation, flight in zip(history, flight_info):
        if flight:
            key = (
                flight.flight_name,
                flight.flight_type,
                flight.departure_date,
                flight.fare,
                flight.id,
            )
            if key not in grouped_data:
                grouped_data[key] = []
            grouped_data[key].append((reservation, flight))

    context = {"grouped_data": grouped_data}
    return render(
        request, "history/user/booking-history/flight-booking-history.html", context
    )


@login_required(login_url="login")
@allowed_users(allowed_roles=["User"])
def flight_travel_history(request):
    user = request.user
    history = FlightReservation.objects.filter(
        reservation_user=user, status="Completed"
    )
    flight_info = []

    for reservation in history:
        trip_id = reservation.trip_id
        try:
            flight = Flight.objects.get(pk=trip_id)
            flight_info.append(flight)
        except Flight.DoesNotExist:
            flight_info.append(None)

    grouped_data = {}
    for reservation, flight in zip(history, flight_info):
        if flight:
            key = (
                flight.flight_name,
                flight.flight_type,
                flight.departure_date,
                flight.fare,
            )
            if key not in grouped_data:
                grouped_data[key] = []
            grouped_data[key].append((reservation, flight))

    context = {"grouped_data": grouped_data}
    return render(
        request, "history/user/travel-history/flight-travel-history.html", context
    )


def flight_reservation_details(request):
    trip_name = request.POST.get("trip_name")
    user = request.user
    flight = get_object_or_404(Flight, flight_name=trip_name)
    reservations = FlightReservation.objects.filter(
        trip_id=flight.id, reservation_user=user, status="Booked"
    )

    reservation_data = []
    for reservation in reservations:
        reservation_data.append(
            {
                "reservation_user": reservation.reservation_user.username,
                "passenger_names": reservation.passenger_names,
                "seat_numbers": reservation.seat_numbers,
                "status": reservation.status,
                "created_at": reservation.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    flight_data = {
        "flight_name": flight.flight_name,
        "flight_type": flight.flight_type,
        "departure_date": flight.departure_date.strftime("%Y-%m-%d"),
        "departure_airport": flight.departure_airport,
        "arrival_airport": flight.arrival_airport,
        "fare": str(flight.fare),
        "max_seats": str(flight.max_seats),
    }

    response_data = {
        "flight_data": flight_data,
        "reservation_data": reservation_data,
    }

    return JsonResponse(response_data)


def flight_reservation_history_details(request):
    trip_name = request.POST.get("trip_name")
    user = request.user
    flight = get_object_or_404(Flight, flight_name=trip_name)
    reservations = FlightReservation.objects.filter(
        trip_id=flight.id, reservation_user=user, status="Completed"
    )

    reservation_data = []
    for reservation in reservations:
        reservation_data.append(
            {
                "reservation_user": reservation.reservation_user.username,
                "passenger_names": reservation.passenger_names,
                "seat_numbers": reservation.seat_numbers,
                "status": reservation.status,
                "created_at": reservation.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    flight_data = {
        "flight_name": flight.flight_name,
        "flight_type": flight.flight_type,
        "departure_date": flight.departure_date.strftime("%Y-%m-%d"),
        "departure_airport": flight.departure_airport,
        "arrival_airport": flight.arrival_airport,
        "fare": str(flight.fare),
        "max_seats": str(flight.max_seats),
    }

    response_data = {
        "flight_data": flight_data,
        "reservation_data": reservation_data,
    }

    return JsonResponse(response_data)


@login_required(login_url="login")
@allowed_users(allowed_roles=["User"])
def train_booking_history(request):
    user = request.user
    history = TrainReservation.objects.filter(reservation_user=user, status="Booked")
    train_info = []

    for reservation in history:
        trip_id = reservation.trip_id
        try:
            train = Train.objects.get(pk=trip_id)
            train_info.append(train)
        except Train.DoesNotExist:
            train_info.append(None)

    grouped_data = {}
    for reservation, train in zip(history, train_info):
        if train:
            key = (
                train.train_name,
                train.train_type,
                train.departure_date,
                train.fare,
                train.run_daily,
                train.id,
            )
            if key not in grouped_data:
                grouped_data[key] = []
            grouped_data[key].append((reservation, train))

    context = {"grouped_data": grouped_data}
    return render(
        request, "history/user/booking-history/train-booking-history.html", context
    )


@login_required(login_url="login")
@allowed_users(allowed_roles=["User"])
def train_travel_history(request):
    user = request.user
    history = TrainReservation.objects.filter(reservation_user=user, status="Completed")
    train_info = []

    for reservation in history:
        trip_id = reservation.trip_id
        try:
            train = Train.objects.get(pk=trip_id)
            train_info.append(train)
        except Train.DoesNotExist:
            train_info.append(None)

    grouped_data = {}
    for reservation, train in zip(history, train_info):
        if train:
            key = (
                train.train_name,
                train.train_type,
                train.departure_date,
                train.fare,
                train.run_daily,
            )
            if key not in grouped_data:
                grouped_data[key] = []
            grouped_data[key].append((reservation, train))

    context = {"grouped_data": grouped_data}
    return render(
        request, "history/user/travel-history/train-travel-history.html", context
    )


def train_reservation_details(request):
    trip_name = request.POST.get("trip_name")
    user = request.user
    train = get_object_or_404(Train, train_name=trip_name)
    reservations = TrainReservation.objects.filter(
        trip_id=train.id, reservation_user=user, status="Booked"
    )

    reservation_data = []
    for reservation in reservations:
        reservation_data.append(
            {
                "reservation_user": reservation.reservation_user.username,
                "passenger_names": reservation.passenger_names,
                "seat_numbers": reservation.seat_numbers,
                "status": reservation.status,
                "created_at": reservation.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    train_data = {
        "train_name": train.train_name,
        "train_type": train.train_type,
        "departure_date": train.departure_date.strftime("%Y-%m-%d"),
        "departure_station": train.departure_station,
        "arrival_station": train.arrival_station,
        "fare": str(train.fare),
        "max_seats": str(train.max_seats),
        "run_daily": train.run_daily,
    }

    response_data = {
        "train_data": train_data,
        "reservation_data": reservation_data,
    }

    return JsonResponse(response_data)


def train_reservation_history_details(request):
    trip_name = request.POST.get("trip_name")
    user = request.user
    train = get_object_or_404(Train, train_name=trip_name)
    reservations = TrainReservation.objects.filter(
        trip_id=train.id, reservation_user=user, status="Completed"
    )

    reservation_data = []
    for reservation in reservations:
        reservation_data.append(
            {
                "reservation_user": reservation.reservation_user.username,
                "passenger_names": reservation.passenger_names,
                "seat_numbers": reservation.seat_numbers,
                "status": reservation.status,
                "created_at": reservation.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    train_data = {
        "train_name": train.train_name,
        "train_type": train.train_type,
        "departure_date": train.departure_date.strftime("%Y-%m-%d"),
        "departure_station": train.departure_station,
        "arrival_station": train.arrival_station,
        "fare": str(train.fare),
        "max_seats": str(train.max_seats),
        "run_daily": train.run_daily,
    }

    response_data = {
        "train_data": train_data,
        "reservation_data": reservation_data,
    }

    return JsonResponse(response_data)
