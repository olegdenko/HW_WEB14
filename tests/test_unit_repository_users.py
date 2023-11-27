import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from main import app
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from src.database.models import User
from src.schemas import UserModel
from src.repository.users import get_user_by_email, create_user, update_avatar, update_token, confirmed_email
from src.database.db import SessionLocal



@pytest.fixture(scope="function")
def db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_get_user_by_email(db: Session):
    # Create a test user
    test_email = "test@example.com"
    test_user = User(email=test_email)
    db.add(test_user)
    db.commit()

    # Test the get_user_by_email function
    user = get_user_by_email(test_email, db)
    assert user is not None
    assert user.email == test_email

def test_create_user(db: Session):
    # Test the create_user function
    user_data = UserModel(username="testuser", email="testuser@example.com", password="testpassword", roles=["user"])
    created_user = create_user(user_data, db)
    assert created_user is not None
    assert created_user.username == "testuser"

# Add similar tests for other functions (update_avatar, update_token, confirmed_email)
