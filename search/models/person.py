from typing import Optional

from pydantic import BaseModel, Field, PositiveInt
from pydantic_extra_types.phone_numbers import PhoneNumber


class Person(BaseModel):
    first_name: str = Field(..., min_length=3, max_length=30)
    last_name: str = Field(..., min_length=3, max_length=30)
    age: PositiveInt = Field(..., description="The age of the person.")
    phone: Optional[PhoneNumber] = Field(default=None, description="The phone number of the person.")
