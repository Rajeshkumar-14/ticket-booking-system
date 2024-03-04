from django.urls import path
from . import views
urlpatterns = [
    path('flight-home/',views.flight_home,name='flight-home'),
    path('check-flight-availability/',views.check_flight_availability,name='check-flight-availability'),
    path('flight-reservation/<int:id>/',views.flight_reservation,name='flight-reservation'),
    path('save-flight-reservation/',views.save_flight_reservation,name='save-flight-reservation'),
    path('cancel-flight-reservation/',views.cancel_flight_reservation,name='cancel-flight-reservation'),
    path('cancel-flight-trip/',views.cancel_flight_trip,name='cancel-flight-trip'),
]