from django.contrib import admin
from .models import Bus, Train, Flight

__project_by__ = "RajeshKumar"

class BusAdmin(admin.ModelAdmin):
    list_display = ('bus_type', 'journey_date', 'start_point', 'end_point', 'user', 'created_at')
    list_filter = ('bus_type', 'journey_date', 'user', 'start_point', 'end_point')
    search_fields = ('bus_type', 'start_point', 'end_point', 'user__username')
    list_per_page = 20
    ordering = ('-created_at',)

class TrainAdmin(admin.ModelAdmin):
    list_display = ('train_type', 'run_daily', 'departure_date', 'departure_station', 'arrival_station', 'user', 'created_at')
    list_filter = ('train_type', 'run_daily', 'departure_station', 'arrival_station', 'user')
    search_fields = ('train_type', 'departure_station', 'arrival_station', 'user__username')
    list_per_page = 20
    ordering = ('-created_at',)

class FlightAdmin(admin.ModelAdmin):
    list_display = ('flight_type', 'departure_date', 'departure_airport', 'arrival_airport', 'user', 'created_at')
    list_filter = ('flight_type', 'departure_airport', 'arrival_airport', 'user')
    search_fields = ('flight_type', 'departure_airport', 'arrival_airport', 'user__username')
    list_per_page = 20
    ordering = ('-created_at',)

admin.site.register(Bus, BusAdmin)
admin.site.register(Train, TrainAdmin)
admin.site.register(Flight, FlightAdmin)
