from django.contrib.auth.models import User
from django.db import models

__project_by__ = "RajeshKumar"


class Bus(models.Model):
    BUS_CHOICES = (
        ("Coach Bus", "Coach Bus"),
        ("Mini Bus", "Mini Bus"),
        ("Tour Bus", "Tour Bus"),
        ("Shuttle Bus", "Shuttle Bus"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="buses")
    bus_name = models.CharField(max_length=200, null=False, blank=False)
    bus_number = models.IntegerField(null=False, blank=False, unique=True)
    bus_type = models.CharField(max_length=20, choices=BUS_CHOICES)
    journey_date = models.DateField(null=False, blank=False)
    start_point = models.CharField(max_length=255, null=False, blank=False)
    end_point = models.CharField(max_length=255, null=False, blank=False)
    fare = models.DecimalField(decimal_places=2, max_digits=10, default="30")
    created_at = models.DateTimeField(auto_now_add=True)
    booking_limit = models.IntegerField(null=False, blank=False, default=5)
    max_seats = models.IntegerField(null=True, blank=True, default=30)
    updated_at = models.DateTimeField(auto_now=True)

    def seats(self, *args, **kwargs):
        if self.bus_type == "Coach Bus":
            self.max_seats = 50
        elif self.bus_type == "Mini Bus":
            self.max_seats = 20
        elif self.bus_type == "Tour Bus":
            self.max_seats = 30
        elif self.bus_type == "Shuttle Bus":
            self.max_seats = 15
        super(Bus, self).save(*args, **kwargs)


class Train(models.Model):
    TRAIN_CHOICES = (
        ("Express Train", "Express Train"),
        ("Local Train", "Local Train"),
        ("High-Speed Train", "High-Speed Train"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trains")
    train_name = models.CharField(max_length=200, null=False, blank=False)
    train_number = models.IntegerField(null=False, blank=False, unique=True)
    train_type = models.CharField(max_length=20, choices=TRAIN_CHOICES)
    run_daily = models.BooleanField(default=False, null=True, blank=True)
    departure_date = models.DateField(null=True, blank=True)
    departure_station = models.CharField(max_length=255, null=False, blank=False)
    arrival_station = models.CharField(max_length=255, null=False, blank=False)
    fare = models.DecimalField(decimal_places=2, max_digits=10, default="50")
    booking_limit = models.IntegerField(null=False, blank=False, default=5)
    max_seats = models.IntegerField(null=True, blank=True, default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def seats(self, *args, **kwargs):
        if self.train_type == "Express Train":
            self.max_seats = 50
        elif self.train_type == "Local Train":
            self.max_seats = 30
        elif self.train_type == "High-Speed Train":
            self.max_seats = 20
        super(Train, self).save(*args, **kwargs)

    def is_daily(self, *args, **kwargs):
        if self.run_daily:
            self.departure_date = None
        super(Train, self).save(*args, **kwargs)


class Flight(models.Model):
    FLIGHT_CHOICES = (
        ("Domestic Flight", "Domestic Flight"),
        ("International Flight", "International Flight"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="flights")
    flight_name = models.CharField(max_length=200, null=False, blank=False)
    flight_number = models.IntegerField(null=False, blank=False, unique=True)
    flight_type = models.CharField(max_length=20, choices=FLIGHT_CHOICES)
    departure_date = models.DateField(null=False, blank=False)
    departure_airport = models.CharField(max_length=255, null=False, blank=False)
    arrival_airport = models.CharField(max_length=255, null=False, blank=False)
    fare = models.DecimalField(decimal_places=2, max_digits=10, default="100")
    created_at = models.DateTimeField(auto_now_add=True)
    booking_limit = models.IntegerField(null=False, blank=False, default=5)
    max_seats = models.IntegerField(null=True, blank=True, default=30)
    updated_at = models.DateTimeField(auto_now=True)

    def seats(self, *args, **kwargs):
        if self.flight_type == "Domestic Flight":
            self.max_seats = 20
        elif self.flight_type == "International Flight":
            self.max_seats = 30
        super(Flight, self).save(*args, **kwargs)
