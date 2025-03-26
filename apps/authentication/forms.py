from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import UserProfile
from .validators import UserProfileValidator

__project_by__ = "RajeshKumar"


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already in use.")
        return email


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["gender", "date_of_birth", "aadhaar_number", "phone_number", "id_proof"]

    def clean(self):
        cleaned_data = super().clean()
        # Use Pydantic validator for additional validation
        pydantic_data = {
            "gender": cleaned_data.get("gender"),
            "date_of_birth": cleaned_data.get("date_of_birth"),
            "aadhaar_number": cleaned_data.get("aadhaar_number"),
            "phone_number": cleaned_data.get("phone_number"),
            "id_proof": cleaned_data.get("id_proof").name if cleaned_data.get("id_proof") else None,
        }
        try:
            validated_data = UserProfileValidator(**pydantic_data).model_dump(exclude_none=True)
        except ValueError as e:
            raise forms.ValidationError(f"Validation error: {str(e)}")
        return cleaned_data

    def clean_id_proof(self):
        id_proof = self.cleaned_data.get("id_proof")
        if id_proof and id_proof.size > 5 * 1024 * 1024:
            raise forms.ValidationError("ID proof file size must be less than 5 MB.")
        return id_proof

    def clean_aadhaar_number(self):
        aadhaar_number = self.cleaned_data.get("aadhaar_number")
        if UserProfile.objects.filter(aadhaar_number=aadhaar_number).exclude(user=self.instance.user).exists():
            raise forms.ValidationError("Aadhaar number already exists.")
        return aadhaar_number

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if UserProfile.objects.filter(phone_number=phone_number).exclude(user=self.instance.user).exists():
            raise forms.ValidationError("Phone number already registered with another account.")
        return phone_number


class ResetPasswordRequestForm(forms.Form):
    email = forms.EmailField(required=True)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("User with this email does not exist.")
        return email