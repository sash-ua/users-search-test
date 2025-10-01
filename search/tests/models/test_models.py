import pytest
from pydantic import ValidationError

from search.models.user import User


def test_user_model_validates():
    u = User(
        username="alice",
        email="alice@example.com",
        description="Hello",
        first_name="Alice",
        last_name="Anderson",
        age=30,
        phone="+12025550123",
    )
    assert u.username == "alice"


def test_user_model_invalid_email_raises():
    with pytest.raises(ValidationError):
        User(
            username="bob",
            email="not-an-email",
            description="Hi",
            first_name="Bob",
            last_name="Brown",
            age=25,
            phone="+12025550123",
        )

