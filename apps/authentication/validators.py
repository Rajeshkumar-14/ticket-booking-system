from datetime import date
from pydantic import BaseModel, Field, field_validator
from typing import Optional

__project_by__ = "RajeshKumar"


class UserProfileValidator(BaseModel):
    gender: str = Field(..., max_length=6)
    date_of_birth: date
    aadhaar_number: str = Field(..., min_length=12, max_length=12)
    phone_number: str = Field(..., min_length=10, max_length=10)
    id_proof: Optional[str] = None

    @field_validator("gender")
    def validate_gender(cls, value):
        valid_genders = ["male", "female", "others"]
        if value not in valid_genders:
            raise ValueError("Gender must be one of: male, female, others.")
        return value

    @field_validator("date_of_birth")
    def validate_date_of_birth(cls, value):
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 0:
            raise ValueError("Date of birth cannot be in the future.")
        if age < 18:
            raise ValueError("User must be at least 18 years old.")
        if age > 120:
            raise ValueError("User age cannot exceed 120 years.")
        return value

    @field_validator("aadhaar_number")
    def validate_aadhaar_number(cls, value):
        if not value.isdigit():
            raise ValueError("Aadhaar number must contain only digits.")
        if len(value) != 12:
            raise ValueError("Aadhaar number must be exactly 12 digits.")
        return value

    @field_validator("phone_number")
    def validate_phone_number(cls, value):
        if not value.isdigit():
            raise ValueError("Phone number must contain only digits.")
        if not value.startswith(("6", "7", "8", "9")):
            raise ValueError("Phone number must start with 6, 7, 8, or 9.")
        return value

    @field_validator("id_proof")
    def validate_id_proof(cls, value):
        if value:
            allowed_extensions = {".jpg", ".jpeg", ".png", ".pdf"}
            extension = f".{value.split('.')[-1].lower()}"
            if extension not in allowed_extensions:
                raise ValueError("ID proof must be a JPG, JPEG, PNG, or PDF file.")
        return value