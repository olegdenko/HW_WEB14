from fastapi import HTTPException
from datetime import timedelta, datetime
from typing import List
from sqlalchemy.orm import Session

from src.database.models import Contact
from src.schemas import (
    ContactModel,
    ContactUpdate,
    ContactStatusUpdate,
    ContactResponse,
)


async def get_contact(contact_id: int, db: Session) -> Contact:
    """
    The get_contact function returns a contact from the database.
        Args:
            contact_id (int): The id of the contact to be returned.
            db (Session): A connection to the database.
        Returns:
            Contact: The requested Contact object.
    
    :param contact_id: int: Get the contact from the database
    :param db: Session: Pass the database session to the function
    :return: A contact object
    :doc-author: Trelent
    """
    return db.query(Contact).filter(Contact.id == contact_id).first()


async def get_contacts(skip: int, limit: int, db: Session) -> List[Contact]:
    """
    The get_contacts function returns a list of contacts from the database.
        
    
    :param skip: int: Specify how many contacts to skip
    :param limit: int: Limit the number of results returned
    :param db: Session: Access the database
    :return: A list of contact objects
    :doc-author: Trelent
    """
    return db.query(Contact).offset(skip).limit(limit).all()


async def get_upcoming_birthdays(db: Session) -> List[ContactResponse]:
    """
    The get_upcoming_birthdays function returns a list of contacts that have birthdays in the next 7 days.
    
    :param db: Session: Pass the database session to the function
    :return: A list of contactresponse objects
    :doc-author: Trelent
    """
    today = datetime.now()
    end_date = today + timedelta(days=7)
    contacts = (
        db.query(Contact)
        .filter(Contact.born_date >= today, Contact.born_date <= end_date)
        .all()
    )
    return [
        ContactResponse(
            id=contact.id,
            name=contact.name,
            last_name=contact.last_name,
            e_mail=contact.e_mail,
            phone_number=contact.phone_number,
            born_date=contact.born_date,
            description=contact.description,
        )
        for contact in contacts
    ]


async def search_contacts(
    name: str, last_name: str, e_mail: str, db: Session
) -> Contact:
    """
    The search_contacts function searches for contacts in the database.
        It takes a name, last_name and e_mail as arguments.
        If any of these are provided, it will search for them in the database.
    
    :param name: str: Search for a contact by name
    :param last_name: str: Filter the contacts by last name
    :param e_mail: str: Search for a contact by e-mail
    :param db: Session: Pass the database session to the function
    :return: A list of contacts
    :doc-author: Trelent
    """
    query = db.query(Contact)

    if name:
        query = query.filter(Contact.name.ilike(f"%{name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if e_mail:
        query = query.filter(Contact.e_mail.ilike(f"%{e_mail}%"))

    contacts = query.all()
    if name and last_name:
        contacts = [
            contact
            for contact in contacts
            if contact.name.lower() == name.lower()
            and contact.last_name.lower() == last_name.lower()
        ]

    if last_name and e_mail:
        contacts = [
            contact
            for contact in contacts
            if contact.last_name.lower() == last_name.lower()
            and contact.e_mail.lower() == e_mail.lower()
        ]

    return contacts


async def create_contact(body: ContactModel, db: Session) -> ContactResponse:
    """
    The create_contact function creates a new contact in the database.
        It takes a ContactModel object as input and returns a ContactResponse object.
        
    
    :param body: ContactModel: Get the data from the request body
    :param db: Session: Create a database session
    :return: A contactresponse object
    :doc-author: Trelent
    """
    try:
        contact = Contact(
            name=body.name,
            last_name=body.last_name,
            e_mail=body.e_mail,
            phone_number=body.phone_number,
            born_date=body.born_date,
            description=body.description,
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)

        return ContactResponse(
            id=contact.id,
            name=contact.name,
            last_name=contact.last_name,
            e_mail=contact.e_mail,
            phone_number=contact.phone_number,
            born_date=contact.born_date,
            description=contact.description,
        )
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=409, detail="Conflict: Something went wrong")


async def remove_contact(contact_id: int, db: Session) -> Contact | None:
    """
    The remove_contact function removes a contact from the database.
        Args:
            contact_id (int): The id of the contact to be removed.
            db (Session): A connection to the database.
        Returns:
            Contact | None: The deleted Contact object or None if no such object exists in the database.
    
    :param contact_id: int: Specify the id of the contact to be deleted
    :param db: Session: Pass the database session to the function
    :return: The contact that was deleted from the database
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def update_contact(
    contact_id: int, body: ContactUpdate, db: Session
) -> Contact | None:
    """
    The update_contact function updates a contact in the database.
        Args:
            contact_id (int): The id of the contact to update.
            body (ContactUpdate): The updated information for the specified Contact.
            db (Session): A connection to our database, used for querying and updating data.
    
    :param contact_id: int: Identify the contact that is going to be updated
    :param body: ContactUpdate: Pass the data from the request body to the function
    :param db: Session: Pass the database session to the function
    :return: The updated contact
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        contact.name = (body.name,)
        contact.last_name = (body.last_name,)
        contact.e_mail = (body.e_mail,)
        contact.phone_number = (body.phone_number,)
        contact.born_date = (body.born_date,)
        contact.description = (body.description,)
        db.commit()
    return contact


async def update_status_contact(
    contact_id: int, body: ContactStatusUpdate, db: Session
) -> Contact | None:
    """
    The update_status_contact function updates the status of a contact in the database.
        
    
    :param contact_id: int: Identify the contact that is being updated
    :param body: ContactStatusUpdate: Update the status of a contact
    :param db: Session: Get access to the database
    :return: The updated contact
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        contact.done = body.done
        db.commit()
    return contact
