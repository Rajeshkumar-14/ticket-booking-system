import json
from datetime import timedelta
from xml.dom import ValidationErr

from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from bus.models import BusReservation
from core.models import Bus, Flight, Train
from flight.models import FlightReservation
from train.models import TrainReservation

from .decorators import allowed_users

__project_by__ = "RajeshKumar"


@login_required(login_url="login")
@allowed_users(allowed_roles=["Administration"])
def administration(request):
    # Total Buses
    total_buses = Bus.objects.count()

    # Buses Running Today
    today = timezone.now().date()
    buses_running_today = Bus.objects.filter(journey_date=today).count()

    # Buses Running This Week
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    buses_running_this_week = Bus.objects.filter(
        journey_date__range=[start_of_week, end_of_week]
    ).count()

    # Total Trains
    total_trains = Train.objects.count()

    # Trains Running Today
    trains_running_today = Train.objects.filter(departure_date=today).count()

    # Trains Running This Week
    trains_running_this_week = Train.objects.filter(
        departure_date__range=[start_of_week, end_of_week]
    ).count()

    # Total Flights
    total_flights = Flight.objects.count()

    # Flights Running Today
    flights_running_today = Flight.objects.filter(departure_date=today).count()

    # Flights Running This Week
    flights_running_this_week = Flight.objects.filter(
        departure_date__range=[start_of_week, end_of_week]
    ).count()
    total_running = total_buses + total_flights + total_trains
    total_running_today = buses_running_today + trains_running_today + flights_running_today
    total_running_this_week = (
        buses_running_this_week + trains_running_this_week + flights_running_this_week
    )
    context = {
        "total_buses": total_buses,
        "buses_running_today": buses_running_today,
        "buses_running_this_week": buses_running_this_week,
        "total_trains": total_trains,
        "trains_running_today": trains_running_today,
        "trains_running_this_week": trains_running_this_week,
        "total_flights": total_flights,
        "flights_running_today": flights_running_today,
        "flights_running_this_week": flights_running_this_week,
        "total_running": total_running,
        "total_running_today": total_running_today,
        "total_running_this_week": total_running_this_week,
    }

    return render(request, "administration/administration.html", context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["Administration"])
def bus_index(request):
    bus_types = Bus.BUS_CHOICES
    buses = Bus.objects.all()
    context = {"buses": buses, "bus_types": bus_types}
    return render(request, "bus-creation/bus-index.html", context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["Administration"])
def create_bus(request):
    if request.method == "POST":
        bus_name = request.POST.get("bus_name")
        bus_number = request.POST.get("bus_number")
        bus_type = request.POST.get("bus_type")
        journey_date = request.POST.get("journey_date")
        start_point = request.POST.get("start_point")
        end_point = request.POST.get("end_point")
        fare = request.POST.get("fare")
        booking_limit = request.POST.get("booking_limit")
        max_seats = request.POST.get("max_seats")

        user = request.user
        new_bus = Bus(
            user=user,
            bus_name=bus_name,
            bus_number=bus_number,
            bus_type=bus_type,
            journey_date=journey_date,
            start_point=start_point,
            end_point=end_point,
            fare=fare,
            booking_limit=booking_limit,
            max_seats=max_seats,
        )

        new_bus.save()

        if request == "POST":
            response_data = {"status": "success", "message": "Bus created successfully"}
            return JsonResponse(response_data)

    return JsonResponse({"status": "error", "message": "Invalid request method"})


@login_required(login_url="login")
@allowed_users(allowed_roles=["Administration"])
def edit_bus(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)
    serialized_bus = serialize("json", [bus])
    bus_data = json.loads(serialized_bus)[0]["fields"]
    bus_data["id"] = bus.id
    context = {"bus": bus_data}
    return JsonResponse(context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["Administration"])
def update_bus(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)

    if request.method == "POST":
        try:
            bus.bus_name = request.POST.get("edit_bus_name")
            bus.bus_number = request.POST.get("edit_bus_number")
            bus.bus_type = request.POST.get("edit_bus_type")
            bus.journey_date = request.POST.get("edit_journey_date")
            bus.start_point = request.POST.get("edit_start_point")
            bus.end_point = request.POST.get("edit_end_point")
            bus.fare = request.POST.get("edit_fare")
            bus.booking_limit = request.POST.get("edit_booking_limit")
            bus.max_seats = request.POST.get("edit_max_seats")

            bus.full_clean()
            bus.save()

            return JsonResponse({"status": "success", "message": "Bus updated successfully!"})
        except ValidationErr as e:
            return JsonResponse({"status": "error", "error": e.message_dict}, status=400)
    else:
        return JsonResponse({"status": "error", "error": "Invalid request method"}, status=400)


@login_required(login_url="login")
@allowed_users(allowed_roles=["Administration"])
def delete_bus(request):
    bus_id = request.POST.get("bus_id")

    try:
        bus = get_object_or_404(Bus, id=bus_id)
        bus.delete()
        message = "Bus deleted successfully."
        status = "success"
    except Bus.DoesNotExist:
        message = "Bus not found."
        status = "error"
    except Exception as e:
        message = f"An error occurred: {str(e)}"
        status = "error"

    return JsonResponse({"message": message, "status": status})


def bus_details(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)
    bus_data = {
        "bus_name": bus.bus_name,
        "bus_number": bus.bus_number,
        "bus_type": bus.bus_type,
        "journey_date": bus.journey_date.strftime("%Y-%m-%d"),
        "start_point": bus.start_point,
        "end_point": bus.end_point,
        "fare": str(bus.fare),
        "booking_limit": bus.booking_limit,
        "max_seats": bus.max_seats,
    }
    return JsonResponse(bus_data)


@login_required(login_url="login")
@allowed_users(allowed_roles=["Administration"])
def bus_history(request):
    history = BusReservation.objects.filter(status="Booked")
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
            key = (bus.bus_name, bus.journey_date, bus.id)
            if key not in grouped_data:
                grouped_data[key] = []
            grouped_data[key].append((reservation, bus))

    context = {"grouped_data": grouped_data}
    return render(request, "history/admin/booking-history/bus-history.html", context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["Administration"])
def bus_travel_history(request):
    history = BusReservation.objects.filter(status="Completed")
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
            key = (bus.bus_name, bus.journey_date, bus.id)
            if key not in grouped_data:
                grouped_data[key] = []
            grouped_data[key].append((reservation, bus))

    context = {"grouped_data": grouped_data}
    return render(request, "history/admin/travel-history/bus-travel-history.html", context)


# FLIGHT


@login_required(login_url="login")
@allowed_users(allowed_roles=["Administration"])
def flight_index(request):
    flight_types = Flight.FLIGHT_CHOICES
    flights = Flight.objects.all()
    context = {"flights": flights, "flight_types": flight_types}
    return render(request, "flight-creation/flight-index.html", context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["Administration"])
def create_flight(request):
    if request.method == "POST":
        flight_name = request.POST.get("flight_name")
        flight_number = request.POST.get("flight_number")
        flight_type = request.POST.get("flight_type")
        departure_date = request.POST.get("departure_date")
        departure_airport = request.POST.get("departure_airport")
        arrival_airport = request.POST.get("arrival_airport")
        fare = request.POST.get("fare")
        booking_limit = request.POST.get("booking_limit")
        max_seats = request.POST.get("max_seats")

        user = request.user
        new_flight = Flight(
            user=user,
            flight_name=flight_name,
            flight_number=flight_number,
            flight_type=flight_type,
            departure_date=departure_date,
            departure_airport=departure_airport,
            arrival_airport=arrival_airport,
            fare=fare,
            booking_limit=booking_limit,
            max_seats=max_seats,
        )

        new_flight.save()

        if request == "POST":
            response_data = {
                "status": "success",
                "message": "Flight created successfully",
            }
            return JsonResponse(response_data)

    return JsonResponse({"status": "error", "message": "Invalid request method"})


@login_required(login_url="login")
@allowed_users(allowed_roles=["Administration"])
def edit_flight(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)

    serialized_flight = serialize("json", [flight])

    flight_data = json.loads(serialized_flight)[0]["fields"]

    flight_data["id"] = flight.id

    context = {"flight": flight_data}
    return JsonResponse(context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["Administration"])
def update_flight(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)

    if request.method == "POST":
        try:
            flight.flight_name = request.POST.get("edit_flight_name")
            flight.flight_number = request.POST.get("edit_flight_number")
            flight.flight_type = request.POST.get("edit_flight_type")
            flight.departure_date = request.POST.get("edit_departure_date")
            flight.departure_airport = request.POST.get("edit_departure_airport")
            flight.arrival_airport = request.POST.get("edit_arrival_airport")
            flight.fare = request.POST.get("edit_fare")
            flight.booking_limit = request.POST.get("edit_booking_limit")
            flight.max_seats = request.POST.get("edit_max_seats")

            flight.full_clean()
            flight.save()

            return JsonResponse({"status": "success", "message": "Flight updated successfully!"})
        except ValidationErr as e:
            return JsonResponse({"status": "error", "error": e.message_dict}, status=400)
    else:
        return JsonResponse({"status": "error", "error": "Invalid request method"}, status=400)


@login_required(login_url="login")
@allowed_users(allowed_roles=["Administration"])
def delete_flight(request):
    flight_id = request.POST.get("flight_id")

    try:
        flight = get_object_or_404(Flight, id=flight_id)
        flight.delete()
        message = "Flight deleted successfully."
        status = "success"
    except Flight.DoesNotExist:
        message = "Flight not found."
        status = "error"
    except Exception as e:
        message = f"An error occurred: {str(e)}"
        status = "error"

    return JsonResponse({"message": message, "status": status})


@login_required(login_url="login")
@allowed_users(allowed_roles=["Administration"])
def flight_details(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    flight_data = {
        "flight_name": flight.flight_name,
        "flight_number": flight.flight_number,
        "flight_type": flight.flight_type,
        "departure_date": flight.departure_date.strftime("%Y-%m-%d"),
        "departure_airport": flight.departure_airport,
        "arrival_airport": flight.arrival_airport,
        "fare": str(flight.fare),
        "booking_limit": flight.booking_limit,
        "max_seats": flight.max_seats,
    }
    return JsonResponse(flight_data)


@login_required(login_url="login")
@allowed_users(allowed_roles=["Administration"])
def flight_history(request):
    history = FlightReservation.objects.filter(status="Booked")
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
                flight.departure_date,
                flight.id,
            )
            if key not in grouped_data:
                grouped_data[key] = []
            grouped_data[key].append((reservation, flight))

    context = {"grouped_data": grouped_data}
    return render(request, "history/admin/booking-history/flight-history.html", context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["Administration"])
def flight_travel_history(request):
    history = FlightReservation.objects.filter(status="Completed")
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
                flight.departure_date,
                flight.id,
            )
            if key not in grouped_data:
                grouped_data[key] = []
            grouped_data[key].append((reservation, flight))

    context = {"grouped_data": grouped_data}
    return render(request, "history/admin/travel-history/flight-travel-history.html", context)


# TRAIN:
@login_required(login_url="login")
@allowed_users(allowed_roles=["Administration"])
def train_index(request):
    train_types = Train.TRAIN_CHOICES
    trains = Train.objects.all()
    context = {"trains": trains, "train_types": train_types}
    return render(request, "train-creation/train-index.html", context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["Administration"])
def create_train(request):
    if request.method == "POST":
        train_name = request.POST.get("train_name")
        train_number = request.POST.get("train_number")
        train_type = request.POST.get("train_type")
        run_daily = request.POST.get("run_daily")
        print(run_daily)
        departure_date = request.POST.get("departure_date")
        departure_station = request.POST.get("departure_station")
        arrival_station = request.POST.get("arrival_station")
        fare = request.POST.get("fare")
        booking_limit = request.POST.get("booking_limit")
        max_seats = request.POST.get("max_seats")
        formated_run_daily = ""
        if run_daily == "on":
            formated_run_daily = True
        else:
            formated_run_daily = False
        user = request.user
        new_train = Train(
            user=user,
            train_name=train_name,
            train_number=train_number,
            train_type=train_type,
            run_daily=formated_run_daily,
            departure_date=departure_date,
            departure_station=departure_station,
            arrival_station=arrival_station,
            fare=fare,
            booking_limit=booking_limit,
            max_seats=max_seats,
        )

        new_train.save()

        if request == "POST":
            response_data = {
                "status": "success",
                "message": "Train created successfully",
            }
            return JsonResponse(response_data)

    return JsonResponse({"status": "error", "message": "Invalid request method"})


@login_required(login_url="login")
@allowed_users(allowed_roles=["Administration"])
def edit_train(request, train_id):
    train = get_object_or_404(Train, id=train_id)

    serialized_train = serialize("json", [train])

    train_data = json.loads(serialized_train)[0]["fields"]

    train_data["id"] = train.id

    context = {"train": train_data}
    return JsonResponse(context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["Administration"])
def update_train(request, train_id):
    train = get_object_or_404(Train, id=train_id)

    if request.method == "POST":
        try:
            train.train_name = request.POST.get("edit_train_name")
            train.train_number = request.POST.get("edit_train_number")
            train.train_type = request.POST.get("edit_train_type")
            run_daily = request.POST.get("edit_run_daily")
            train.departure_date = request.POST.get("edit_departure_date")
            train.departure_station = request.POST.get("edit_departure_station")
            train.arrival_station = request.POST.get("edit_arrival_station")
            train.fare = request.POST.get("edit_fare")
            train.booking_limit = request.POST.get("edit_booking_limit")
            train.max_seats = request.POST.get("edit_max_seats")
            formated_run_daily = ""
            if run_daily == "on":
                formated_run_daily = True
            else:
                formated_run_daily = False
            train.run_daily = formated_run_daily
            train.full_clean()
            train.save()

            return JsonResponse({"status": "success", "message": "Train updated successfully!"})
        except ValidationErr as e:
            return JsonResponse({"status": "error", "error": e.message_dict}, status=400)
    else:
        return JsonResponse({"status": "error", "error": "Invalid request method"}, status=400)


@login_required(login_url="login")
@allowed_users(allowed_roles=["Administration"])
def delete_train(request):
    train_id = request.POST.get("train_id")

    try:
        train = get_object_or_404(Train, id=train_id)
        train.delete()
        message = "Train deleted successfully."
        status = "success"
    except Train.DoesNotExist:
        message = "Train not found."
        status = "error"
    except Exception as e:
        message = f"An error occurred: {str(e)}"
        status = "error"

    return JsonResponse({"message": message, "status": status})


@login_required(login_url="login")
@allowed_users(allowed_roles=["Administration"])
def train_details(request, train_id):
    train = get_object_or_404(Train, id=train_id)
    train_data = {
        "train_name": train.train_name,
        "train_number": train.train_number,
        "train_type": train.train_type,
        "run_daily": train.run_daily,
        "departure_date": (
            train.departure_date.strftime("%Y-%m-%d") if train.departure_date else None
        ),
        "departure_station": train.departure_station,
        "arrival_station": train.arrival_station,
        "fare": str(train.fare),
        "booking_limit": train.booking_limit,
        "max_seats": train.max_seats,
    }
    return JsonResponse(train_data)


@login_required(login_url="login")
@allowed_users(allowed_roles=["Administration"])
def train_history(request):
    history = TrainReservation.objects.filter(status="Booked")
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
                train.departure_date,
                train.id,
            )
            if key not in grouped_data:
                grouped_data[key] = []
            grouped_data[key].append((reservation, train))

    context = {"grouped_data": grouped_data}
    return render(request, "history/admin/booking-history/train-history.html", context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["Administration"])
def train_travel_history(request):
    history = TrainReservation.objects.filter(status="Completed")
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
                train.departure_date,
                train.id,
            )
            if key not in grouped_data:
                grouped_data[key] = []
            grouped_data[key].append((reservation, train))

    context = {"grouped_data": grouped_data}
    return render(request, "history/admin/travel-history/train-travel-history.html", context)
