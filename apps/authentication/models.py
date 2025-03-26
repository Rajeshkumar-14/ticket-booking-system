# apps/authentication/models.py
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator, RegexValidator
from django.db import models
from encrypted_model_fields.fields import EncryptedCharField

__project_by__ = "RajeshKumar"


class UserProfile(models.Model):
    GENDER_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
        ("others", "Others"),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    gender = models.CharField(
        max_length=6,
        choices=GENDER_CHOICES,
        null=False,
        blank=False,
    )
    date_of_birth = models.DateField(
        null=False,
        blank=False,
    )
    aadhaar_number = EncryptedCharField(
        max_length=16,
        unique=True,
        null=False,
        blank=False,
    )
    phone_number = models.CharField(
        max_length=10,
        null=False,
        blank=False,
        validators=[
            RegexValidator(
                regex=r"^[6-9]\d{9}$",
                message="Phone number must be a valid 10-digit Indian number starting with 6-9.",
            )
        ],
        db_index=True, 
    )
    id_proof = models.FileField(
        upload_to="proof/",
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "pdf"])],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

    class Meta:
        indexes = [
            models.Index(fields=["phone_number"]), 
        ]