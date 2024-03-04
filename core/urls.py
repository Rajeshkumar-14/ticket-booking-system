from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("bus-booking-history/", views.bus_booking_history, name="bus-booking-history"),
    path("bus-travel-history/", views.bus_travel_history, name="bus-travel-history"),
    path('bus-reservation-details',views.bus_reservation_details,name='bus-reservation-details'),
    path('bus-reservation-history-details',views.bus_reservation_history_details,name='bus-reservation-history-details'),
    path("flight-booking-history/", views.flight_booking_history, name="flight-booking-history"),
    path("flight-travel-history/", views.flight_travel_history, name="flight-travel-history"),
    path('flight-reservation-details',views.flight_reservation_details,name='flight-reservation-details'),
    path('flight-reservation-history-details',views.flight_reservation_history_details,name='flight-reservation-history-details'),
    path("train-booking-history/", views.train_booking_history, name="train-booking-history"),
    path("train-travel-history/", views.train_travel_history, name="train-travel-history"),
    path('train-reservation-details',views.train_reservation_details,name='train-reservation-details'),
    path('train-reservation-history-details',views.train_reservation_history_details,name='train-reservation-history-details'),
]
