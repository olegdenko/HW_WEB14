import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(str(Path(__file__).parent.parent))
from src.repository import auth
from src.database.db import Base, get_db

# Replace with the path to your configuration file
settings_path = "path/to/your/settings.yaml"
# Create a test database engine
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


# Override dependency to use the test database
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app = TestClient(auth.app)


# Test cases go here

# Example test case
def test_create_access_token():
    data = {"sub": "test@example.com", "scope": "access_token"}
    access_token = auth.create_access_token(data)
    assert isinstance(access_token, str)
    # You can add more assertions based on your requirements


# Example test case using dependency override
@pytest.mark.dependency(depends=["test_create_access_token"])
def test_protected_endpoint():
    # Mock token for testing purposes
    mock_token = "mock_access_token"
    response = app.get("/protected-endpoint", headers={"Authorization": f"Bearer {mock_token}"})
    assert response.status_code == 200
    # You can add more assertions based on your requirements
