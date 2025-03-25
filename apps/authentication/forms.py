from django import forms
from django.contrib.auth.models import User

from utils.constants import AUTH_ERROR_MESSAGES

from .models import UserProfile


class RegistrationForm(forms.Form):
    print("RegistrationForm")
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    password1 = forms.CharField(
        widget=forms.PasswordInput, required=True, label="Confirm Password"
    )
    phone_number = forms.CharField(max_length=10, required=True)

    def clean_username(self):
        print("clean_username")
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(AUTH_ERROR_MESSAGES["USERNAME_EXISTS"])
        return username

    def clean_email(self):
        print("clean_email")
        email = self.cleaned_data["email"].strip()
        print(email)
        if User.objects.filter(email=email).exists():
            print("email exists")
            raise forms.ValidationError(AUTH_ERROR_MESSAGES["EMAIL_EXISTS"])
        return email

    def clean_phone_number(self):
        print("clean_phone_number")
        phone_number = self.cleaned_data["phone_number"].strip()
        print(phone_number)
        if UserProfile.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError(AUTH_ERROR_MESSAGES["PHONE_EXISTS"])
        if not phone_number.isdigit() or len(phone_number) != 10:
            raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return phone_number

    def clean(self):
        print("clean method called")
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password1 = cleaned_data.get("password1")
        print(f"password: {password}, password1: {password1}")
        if password and password1 and password != password1:
            print("Passwords do not match")
            raise forms.ValidationError(AUTH_ERROR_MESSAGES["PASSWORDS_MISMATCH"])
        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "gender",
            "date_of_birth",
            "aadhaar_number",
            "id_number",
            "phone_number",
            "street_address",
            "city",
            "state",
            "country",
            "postal_code",
            "preferred_payment_method",
            "emergency_contact",
        ]

    def clean_aadhaar_number(self):
        aadhaar_number = self.cleaned_data.get("aadhaar_number")
        if (
            aadhaar_number
            and UserProfile.objects.filter(aadhaar_number=aadhaar_number)
            .exclude(user=self.instance.user)
            .exists()
        ):
            raise forms.ValidationError("Aadhaar number already exists.")
        if aadhaar_number and (not aadhaar_number.isdigit() or len(aadhaar_number) != 12):
            raise forms.ValidationError("Aadhaar number must be exactly 12 digits.")
        return aadhaar_number

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if (
            phone_number
            and UserProfile.objects.filter(phone_number=phone_number)
            .exclude(user=self.instance.user)
            .exists()
        ):
            raise forms.ValidationError(AUTH_ERROR_MESSAGES["PHONE_EXISTS"])
        if phone_number and (not phone_number.isdigit() or len(phone_number) != 10):
            raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return phone_number

    def clean_emergency_contact(self):
        emergency_contact = self.cleaned_data.get("emergency_contact")
        if emergency_contact and not (
            emergency_contact.startswith("+")
            and emergency_contact[1:].isdigit()
            or emergency_contact.isdigit()
        ):
            raise forms.ValidationError(
                "Emergency contact must be a valid phone number (10-15 digits, optional country code)."
            )
        if emergency_contact and len(emergency_contact.replace("+", "")) not in range(10, 16):
            raise forms.ValidationError("Emergency contact must be between 10 and 15 digits.")
        return emergency_contact
