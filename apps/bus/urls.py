from django.urls import path

from . import views

app_name = "bus"

urlpatterns = [
    path('bus-home/', views.bus_home, name='bus-home'),
    path('check-bus-availability/', views.check_bus_availability, name='check-bus-availability'),
    path('bus-reservation/<int:id>/', views.bus_reservation, name='bus-reservation'),
    path('save-bus-reservation/', views.save_bus_reservation, name='save-bus-reservation'),
    path('cancel-bus-reservation/', views.cancel_bus_reservation, name='cancel-bus-reservation'),
    path('cancel-bus-trip/', views.cancel_bus_trip, name='cancel-bus-trip'),
]
