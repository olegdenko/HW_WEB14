from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter

from sqlalchemy.orm import Session

from src.database.models import Role, User
from src.database.db import get_db
from src.schemas import (
    ContactModel,
    ContactUpdate,
    ContactResponse,
)
from src.repository import contacts as repository_contacts
from src.services.auth import auth_servise
from src.services.roles import RoleAccess


router = APIRouter(prefix="/contacts", tags=["contacts"])

allowed_operation_get = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_create = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_update = RoleAccess([Role.admin, Role.moderator])
allowed_operation_remove = RoleAccess([Role.admin])


@router.get(
    "/",
    response_model=List[ContactResponse],
    dependencies=[
        Depends(allowed_operation_get),
        Depends(RateLimiter(times=10, seconds=60)),
    ],
    description="No more than 10 requests per minute",
)
async def read_contacts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_servise.get_current_user),
):
    """
    The read_contacts function returns a list of contacts.
        ---
        get:
          summary: Returns a list of contacts.
          tags:
            - Contacts
          parameters:
            - in: query
              name: skip (optional)  # The name parameter is the variable that will be used to pass the value into the function. In this case, it's called &quot;skip&quot;. It's also possible to use an alias for this parameter by using &quot;name&quot; and then specifying an alternative name with &quot;as&quot;. For example, you could use `name=skip&amp;amp;as=offset
    
    :param skip: int: Skip the first n contacts
    :param limit: int: Limit the number of contacts returned
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the user who is currently logged in
    :param : Get the current user from the database
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_contacts(skip, limit, db)
    return contacts


@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
    dependencies=[Depends(allowed_operation_get)],
)
async def read_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_servise.get_current_user),
):
    """
    The read_contact function returns a contact by its ID.
    
    :param contact_id: int: Get the contact id from the url path
    :param db: Session: Pass the database connection to the function
    :param current_user: User: Get the current user from the database
    :param : Get the contact id from the url
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact(contact_id, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.get(
    "/search_by/",
    response_model=List[ContactResponse],
    dependencies=[Depends(allowed_operation_get)],
)
async def search_contact(
    name: str = None,
    last_name: str = None,
    e_mail: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_servise.get_current_user),
):
    """
    The search_contact function searches for a contact in the database.
        Args:
            name (str): The name of the contact to search for.
            last_name (str): The last_name of the contact to search for.
            e_mail (str): The e-mail address of the user to search for.
    
    :param name: str: Search for a contact by name
    :param last_name: str: Search for a contact by last name
    :param e_mail: str: Search for a contact by e-mail
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user
    :param : Get the data from the database
    :return: A list of contacts
    :doc-author: Trelent
    """
    contact = await repository_contacts.search_contacts(name, last_name, e_mail, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.get(
    "/upcoming_birthdays/",
    response_model=List[ContactResponse],
    dependencies=[Depends(allowed_operation_get)],
)
async def read_upcoming_birthdays(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_servise.get_current_user),
):
    """
    The read_upcoming_birthdays function returns a list of contacts with upcoming birthdays.
        The function is called by the read_upcoming_birthdays endpoint, which is defined in the app/main.py file.
    
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the currently logged in user
    :param : Pass the database session to the function
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_upcoming_birthdays(db)
    if contacts is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contacts not found"
        )
    return contacts


@router.post(
    "/",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(allowed_operation_create), Depends(RateLimiter(times=2, seconds=5))]
)
async def create_contact(
    body: ContactModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_servise.get_current_user)):
    """
    The create_contact function creates a new contact in the database.
        The function takes a ContactModel object as input and returns the newly created contact.
    
    
    :param body: ContactModel: Get the data from the request body
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the user that is currently logged in
    :return: A contactmodel object
    :doc-author: Trelent
    """
    return await repository_contacts.create_contact(body, db)


@router.put(
    "/{contact_id}",
    response_model=ContactResponse,
    dependencies=[Depends(allowed_operation_update)],
    description="Only moderator and admin",
)
async def update_contact(
    body: ContactUpdate,
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_servise.get_current_user),
):
    """
    The update_contact function updates a contact in the database.
        The function takes an id and a body as input, and returns the updated contact.
        If no contact is found with that id, it raises an HTTP 404 error.
    
    :param body: ContactUpdate: Get the data from the request body
    :param contact_id: int: Identify the contact to be updated
    :param db: Session: Pass the database session to the repository
    :param current_user: User: Check if the user is logged in
    :param : Get the contact id from the url
    :return: A contactupdate object
    :doc-author: Trelent
    """
    contact = await repository_contacts.update_contact(contact_id, body, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete(
    "/{contact_id}",
    response_model=ContactResponse,
    dependencies=[Depends(allowed_operation_remove)],
)
async def remove_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_servise.get_current_user),
):
    """
    The remove_contact function removes a contact from the database.
        Args:
            contact_id (int): The id of the contact to remove.
            db (Session, optional): SQLAlchemy Session. Defaults to Depends(get_db).
            current_user (User, optional): User object for authentication and authorization purposes. Defaults to Depends(auth_servise.get_current_user).
    
    :param contact_id: int: Pass the contact_id to the function
    :param db: Session: Get the database session
    :param current_user: User: Get the user information from the token
    :param : Get the id of the contact to be removed
    :return: The contact object that was deleted
    :doc-author: Trelent
    """
    contact = await repository_contacts.remove_contact(contact_id, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
