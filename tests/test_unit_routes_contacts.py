import pytest
import sys
from fastapi import Depends
from pathlib import Path
from enum import Enum
import json
from typing import List

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles

sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker

from src.database.models import User
from src.database.db import get_db
from main import app
from src.schemas import ContactModel, ContactUpdate, ContactResponse
from src.services.auth import auth_servise
from src.repository import contacts as repository_contacts

class Role(str, Enum):
    user = "user"
    admin = "admin"

from tests.test_config import DATABASE_URL

test_client = TestClient(app)
test_user = User(id=1, username="testuser", email="test@example.com")  # Role   role=Role.user.value

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base: DeclarativeMeta = declarative_base()

def get_test_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def db_session():
    db = get_test_db()
    try:
        yield db
    finally:
        db.close()


def test_read_contacts(db_session):
    repository_contacts.get_contacts = lambda skip, limit, db: [
        ContactResponse(id=1, name="Test Contact", email="test@example.com")
    ]

    response = test_client.get("/contacts/", headers={"X-Forwarded-For": "127.0.0.1"})  # Assuming your API endpoint is at "/contacts/"

    assert response.status_code == 200
    contacts = response.json()
    assert isinstance(contacts, List)
    assert len(contacts) == 1
    assert contacts[0]["name"] == "Test Contact"


def test_search_contact():
    repository_contacts.search_contacts = lambda name, last_name, e_mail, db: [
        ContactResponse(id=1, name="Test Contact", email="test@example.com")
    ]

    response = test_client.get("/search_by/?name=test", headers={"X-Forwarded-For": "127.0.0.1"})  # Assuming your API endpoint is at "/contacts/search_by/"

    assert response.status_code == 200
    contacts = response.json()
    assert isinstance(contacts, List)
    assert len(contacts) == 1
    assert contacts[0]["name"] == "Test Contact"


def test_read_upcoming_birthdays():
    repository_contacts.get_upcoming_birthdays = lambda db: [
        ContactResponse(id=1, name="Test Contact", email="test@example.com")
    ]

    response = test_client.get("/upcoming_birthdays/", headers={"X-Forwarded-For": "127.0.0.1"})  # Assuming your API endpoint is at "/contacts/upcoming_birthdays/"

    assert response.status_code == 200
    contacts = response.json()
    assert isinstance(contacts, List)
    assert len(contacts) == 1
    assert contacts[0]["name"] == "Test Contact"


def test_create_contact():
    repository_contacts.create_contact = lambda body, db: ContactResponse(
        id=1, name=body.name, email=body.email
    )

    contact_data = {"name": "New Contact", "email": "new@example.com"}
    response = test_client.post("/", json=contact_data, headers={"X-Forwarded-For": "127.0.0.1"})  # Assuming your API endpoint is at "/contacts/"

    assert response.status_code == 201
    contact = response.json()
    assert contact["name"] == "New Contact"


def test_update_contact():
    repository_contacts.update_contact = lambda contact_id, body, db: ContactResponse(
        id=contact_id, name=body.name, email=body.email
    )

    contact_data = {"name": "Updated Contact", "email": "updated@example.com"}
    response = test_client.put("/1", json=contact_data, headers={"X-Forwarded-For": "127.0.0.1"})  # Assuming your API endpoint is at "/contacts/1"

    assert response.status_code == 200
    contact = response.json()
    assert contact["name"] == "Updated Contact"


def test_remove_contact():
    repository_contacts.remove_contact = lambda contact_id, db: ContactResponse(
        id=contact_id, name="Deleted Contact", email="deleted@example.com"
    )

    response = test_client.delete("/1", headers={"X-Forwarded-For": "127.0.0.1"})

    assert response.status_code == 200


if get_test_db in app.dependency_overrides:
    del app.dependency_overrides[get_test_db]
