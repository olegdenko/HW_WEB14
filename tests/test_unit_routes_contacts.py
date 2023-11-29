import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.routes.contacts import router
from src.schemas import ContactModel, ContactUpdate
from src.services.auth import auth_servise
from src.database.models import Contact, Role, User
from src.repository import contacts as repository_contacts


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()



app = TestClient(router)


def test_read_contacts(monkeypatch):
    # Mock the get_contacts function to return a list of contacts
    async def mock_get_contacts(skip: int, limit: int, db: Session):
        return [Contact(), Contact(), Contact()]

    monkeypatch.setattr("src.routes.contacts.get_contacts", mock_get_contacts)

    response = app.get("/contacts/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 3


def test_read_contact(monkeypatch):
    # Mock the get_contact function to return a contact
    async def mock_get_contact(contact_id: int, db: Session):
        return Contact()

    monkeypatch.setattr("src.routes.contacts.get_contact", mock_get_contact)

    response = app.get("/contacts/1")
    assert response.status_code == 200
    assert "id" in response.json()


def test_search_contact(monkeypatch):
    # Mock the search_contacts function to return a list of contacts
    async def mock_search_contacts(name: str, last_name: str, e_mail: str, db: Session):
        return [Contact(), Contact()]

    monkeypatch.setattr("src.routes.contacts.search_contacts", mock_search_contacts)

    response = app.get("/contacts/search_by/?name=test")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2


def test_read_upcoming_birthdays(monkeypatch):
    # Mock the get_upcoming_birthdays function to return a list of contacts
    async def mock_get_upcoming_birthdays(db: Session):
        return [Contact(), Contact()]

    monkeypatch.setattr("src.routes.contacts.get_upcoming_birthdays", mock_get_upcoming_birthdays)

    response = app.get("/contacts/upcoming_birthdays/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2


def test_create_contact(monkeypatch):
    # Mock the create_contact function to return a contact response
    async def mock_create_contact(body: ContactModel, db: Session):
        return ContactModel(**body.dict(), id=1)

    monkeypatch.setattr("src.routes.contacts.create_contact", mock_create_contact)

    contact_data = {
        "name": "John",
        "last_name": "Doe",
        "e_mail": "john.doe@example.com",
        "birthday": "1990-01-01",
    }
    response = app.post("/contacts/", json=contact_data)
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["name"] == contact_data["name"]


def test_update_contact(monkeypatch):
    # Mock the update_contact function to return an updated contact
    async def mock_update_contact(contact_id: int, body: ContactUpdate, db: Session):
        return Contact(id=contact_id, name=body.name)

    monkeypatch.setattr("src.routes.contacts.update_contact", mock_update_contact)

    contact_id = 1
    update_data = {"name": "UpdatedName"}
    response = app.put(f"/contacts/{contact_id}", json=update_data)
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["name"] == update_data["name"]


def test_remove_contact(monkeypatch):
    # Mock the remove_contact function to return the removed contact
    async def mock_remove_contact(contact_id: int, db: Session):
        return Contact(id=contact_id, name="John")

    monkeypatch.setattr("src.routes.contacts.remove_contact", mock_remove_contact)

    contact_id = 1
    response = app.delete(f"/contacts/{contact_id}")
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["name"] == "John"