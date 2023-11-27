from sqlalchemy.orm import Session
from libgravatar import Gravatar
from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email, db: Session) -> User | None:
    """
    The get_user_by_email function takes in an email and a database session,
    and returns the user associated with that email. If no such user exists,
    it returns None.
    
    :param email: Filter the database and find a user with that email
    :param db: Session: Pass the database session to the function
    :return: The first user with the given email
    :doc-author: Trelent
    """
    return db.query(User).filter_by(email=email).first()


async def create_user(body: UserModel, db: Session):
    """
    The create_user function creates a new user in the database.
        
    
    :param body: UserModel: Pass the user data to the function
    :param db: Session: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
    g = Gravatar(body.email)
    # new_user = User(**body.model_dump(), avatar=g.get_image())
    # new_user = User(**body.model_dump(), avatar=g.get_image(), roles=["user"])
    new_user = User(
        username=body.username,
        email=body.email,
        password=body.password,
        avatar=g.get_image(),
        roles=["user"],
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_avatar(email, url: str, db: Session) -> User:
    """
    The update_avatar function updates the avatar of a user.
    
    Args:
        email (str): The email address of the user to update.
        url (str): The URL for the new avatar image.
        db (Session, optional): A database session object to use instead of creating one locally. Defaults to None.  # noQA: E501 line too long
    
    :param email: Find the user in the database
    :param url: str: Specify the type of data that will be passed into the function
    :param db: Session: Pass the database session to the function
    :return: The user object with the updated avatar url
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


async def update_token(user: User, refresh_token, db: Session):
    """
    The update_token function updates the user's refresh token in the database.
        Args:
            user (User): The User object to update.
            refresh_token (str): The new refresh token for this user.
            db (Session): A database session to use for updating the User object.
    
    :param user: User: Find the user in the database
    :param refresh_token: Update the refresh_token in the database
    :param db: Session: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
    user.refresh_token = refresh_token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function sets the confirmed field of a user to True.
    
    :param email: str: Get the email of the user
    :param db: Session: Pass in the database session
    :return: None
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()
