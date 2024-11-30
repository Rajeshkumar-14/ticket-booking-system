from django.db import models
from django.contrib.auth.models import User

class BusReservation(models.Model):
    STATUS = (
        ("Booked", "Booked"),
        ("Completed", "Completed"),
    )
    reservation_user = models.ForeignKey(User, on_delete=models.CASCADE)
    trip_id = models.IntegerField(null=False, blank=False)
    seat_numbers = models.TextField(null=False, blank=False)
    passenger_names = models.TextField(null=False, blank=False)
    id_proof = models.FileField(upload_to="proof/", null=False, blank=False)
    status = models.CharField(max_length=255, choices=STATUS, default="Booked")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.passenger_names}-{self.status}"
