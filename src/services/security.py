from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.conf.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    The get_current_user function is a dependency that will be called by FastAPI to get the current user.
    It uses the OAuth2 Dependency to retrieve the token from the Authorization header, and then validates it with PyJWT.
    
    :param token: str: Pass the token to the function
    :return: A dictionary with the following keys:
    :doc-author: Trelent
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        raise credentials_exception


def create_reset_password_token(email: str) -> str:
    """
    The create_reset_password_token function creates a JWT token that is used to reset the user's password.
        The token contains the email of the user and an expiration date.
        Args:
            email (str): The email of the user who wants to reset their password.
        Returns:
            str: A JWT token containing information about which account should be updated and when it expires.
    
    :param email: str: Specify the email of the user who is requesting a password reset
    :return: A string
    :doc-author: Trelent
    """
    expires_delta = timedelta(minutes=settings.reset_password_token_expire_minutes)
    expire = datetime.utcnow() + expires_delta
    to_encode = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt
