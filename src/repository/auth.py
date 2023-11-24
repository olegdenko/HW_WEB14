from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from jose import JWTError, jwt
from starlette import status

from src.database.models import User
from src.database.db import get_db
from src.conf.config import settings


class Hash:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
        The verify_password function takes a plain-text password and the hashed version of that password,
            and returns True if they match, False otherwise. This is used to verify that the user's login
            credentials are correct.
        
        :param self: Represent the instance of the class
        :param plain_password: Check the password entered by the user
        :param hashed_password: Compare the hashed password in the database with the plain text password that is entered by a user
        :return: True or false depending on whether the password is correct
        :doc-author: Trelent
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        The get_password_hash function takes a password as input and returns the hash of that password.
            The function uses the pwd_context object to generate a hash from the given password.
        
        :param self: Represent the instance of the class
        :param password: str: Get the password from the user
        :return: A hashed password
        :doc-author: Trelent
        """
        return self.pwd_context.hash(password)


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# define a function to generate a new access token
async def create_access_token(data: dict, expires_delta: Optional[float] = None):
    """
    The create_access_token function creates a new access token for the user.
        
    
    :param data: dict: Store the data that will be encoded in the jwt
    :param expires_delta: Optional[float]: Set the expiration time of the access token
    :return: A jwt token that contains the data passed to it
    :doc-author: Trelent
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
    encoded_access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_access_token


# define a function to generate a new refresh token
async def create_refresh_token(data: dict, expires_delta: Optional[float] = None):
    """
    The create_refresh_token function creates a refresh token for the user.
        Args:
            data (dict): The data to be encoded in the JWT. This should include at least a username and an email address, but can also include other information such as roles or permissions.
            expires_delta (Optional[float]): The number of seconds until this token expires, defaults to 7 days if not specified.
    
    :param data: dict: Pass the user's id and username to the function
    :param expires_delta: Optional[float]: Set the expiration time of the refresh token
    :return: A jwt token that is encoded with the user's id, 
    :doc-author: Trelent
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update(
        {"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"}
    )
    encoded_refresh_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_refresh_token


async def get_email_form_refresh_token(refresh_token: str):
    """
    The get_email_form_refresh_token function takes a refresh token and returns the email address associated with it.
        If the refresh token is invalid, an HTTPException is raised.
    
    :param refresh_token: str: Pass the refresh token to this function
    :return: The email of the user
    :doc-author: Trelent
    """
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload["scope"] == "refresh_token":
            email = payload["sub"]
            return email
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope for token"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    The get_current_user function is a dependency that will be used in the protected endpoints.
    It takes an access token as input and returns the user object if it's valid, otherwise raises an exception.
    
    :param token: str: Get the token from the authorization header
    :param db: Session: Get the database session
    :return: The user object
    :doc-author: Trelent
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload["scope"] == "access_token":
            email = payload["sub"]
            if email is None:
                raise credentials_exception
        else:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception

    user: User = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
