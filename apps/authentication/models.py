from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from encrypted_model_fields.fields import EncryptedCharField

__project_by__ = "RajeshKumar"


class UserProfile(models.Model):
    GENDER = (
        ("male", "Male"),
        ("female", "Female"),
        ("others", "Others"),
    )

    PAYMENT_METHODS = (
        ("credit_card", "Credit Card"),
        ("upi", "UPI"),
        ("wallet", "Wallet"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=6, choices=GENDER, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    aadhaar_number = EncryptedCharField(
        max_length=12,
        unique=True,
        null=True,
        blank=True,
        validators=[
            RegexValidator(regex=r'^\d{12}$', message="Aadhaar number must be exactly 12 digits.")
        ],
    )

    phone_number = models.CharField(
        max_length=10,
        null=False,
        blank=False,
        validators=[
            RegexValidator(regex=r'^\d{10}$', message="Phone number must be exactly 10 digits.")
        ],
    )

    id_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Enter your passport number, driver's license number, or other ID number.",
    )

    street_address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)

    preferred_payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        null=True,
        blank=True,
    )

    emergency_contact = EncryptedCharField(
        max_length=15,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?\d{10,15}$',
                message="Emergency contact must be a valid phone number (10-15 digits, optional country code).",
            )
        ],
        help_text="Enter an emergency contact number (e.g., +919876543210).",
    )

    profile_completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return self.user.username

    @property
    def age(self):
        """Calculate age dynamically from date_of_birth."""
        if not self.date_of_birth:
            return None
        from datetime import date

        today = date.today()
        return (
            today.year
            - self.date_of_birth.year
            - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        )

    def is_profile_complete(self):
        """Check if the user has completed their profile."""
        required_fields = [self.phone_number]
        return all(field is not None for field in required_fields)
