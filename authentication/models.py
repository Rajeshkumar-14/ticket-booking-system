from django.contrib.auth.models import User
from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator,
)
from django.db import models

__project_by__ = "RajeshKumar"


class UserProfile(models.Model):
    GENDER = (
        ("male", "Male"),
        ("female", "Female"),
        ("others", "Others"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=6, choices=GENDER, null=False, blank=False)
    age = models.IntegerField(null=False, blank=False)
    date_of_birth = models.DateField(null=False, blank=False)

    aadhaar_number = models.PositiveIntegerField(
        unique=True,
        null=False,
        blank=False,
        validators=[MaxValueValidator(999999999999999)],
    )

    phone_number = models.CharField(max_length=10, null=False, blank=False)

    id_proof = models.FileField(
        upload_to="proof/",
        null=False,
        blank=False,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "pdf"])],
    )

    def __str__(self):
        return self.user.username
