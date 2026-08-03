import re
from pydantic import BaseModel, EmailStr, field_validator

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()

        if len(value) < 4 :
            raise ValueError("Name minimum 4 character")
        
        if len(value) > 16 :
            raise ValueError("Name maximum 16 characters")
        
        if " " in value:
            raise ValueError("Name cannot contain space")
        
        if not re.search(r"[A-Za-z]", value):
            raise ValueError("Name must contain at least 1 letter")
        
        if not re.search(r"\d", value):
            raise ValueError("Name must contain at least 1 number")
        
        if not re.match(r"^[A-Za-z0-9._]+$", value):
            raise ValueError("Name can only contain letters, number, dots, and underscore")
        
        return value
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        
        if len(value) < 8:
            raise ValueError("Password minimum 8 characters")

        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain uppercase letter")

        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain lowercase letter")

        if not re.search(r"\d", value):
            raise ValueError("Password must contain number")

        return value

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
