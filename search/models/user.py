from pydantic import Field, EmailStr
from .person import Person


class User(Person):
    username: str = Field(..., min_length=3, max_length=30, description="Unique user name")
    email: EmailStr = Field(..., max_length=254, description="Email address")
    description: str = Field(description="Description")
