from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Security,
    Header,
    BackgroundTasks,
    Request,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session
from src.services.e_mail import send_email
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail

from src.database.db import get_db
from src.repository import users as repository_users
from src.services.auth import auth_servise


# hash_handler = Hash()
security = HTTPBearer()
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    body: UserModel,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    The signup function creates a new user in the database.
    
    :param body: UserModel: Get the data from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url of the request
    :param db: Session: Get the database session
    :param : Pass the user's email to the function
    :return: A userresponse object
    :doc-author: Trelent
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    body.password = auth_servise.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)

    background_tasks.add_task(
        send_email, new_user.email, new_user.username, str(request.base_url)
    )  # передає урл, на який потрібно перейти для підтверження акаунту

    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        avatar=new_user.avatar,
        roles=new_user.roles,
    )


@router.post("/login", response_model=TokenModel)
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    The login function is used to authenticate a user.
    
    :param body: OAuth2PasswordRequestForm: Get the data from the request body
    :param db: Session: Pass the database session to the function
    :return: A dict, which is a json object
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="401 UNAUTHORIZED Invalid email",
        )
    if not auth_servise.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="401 UNAUTHORIZED Invalid password",
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed"
        )

    # Generate JWT
    access_token = await auth_servise.create_access_token(data={"sub": user.email})
    refresh_token = await auth_servise.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    The confirmed_email function confirms the user's email address.
        Args:
            token (str): The JWT token that was sent to the user's email address.
            db (Session, optional): SQLAlchemy Session. Defaults to Depends(get_db).
    
    :param token: str: Get the token from the url
    :param db: Session: Pass the database connection to the function
    :return: The following error:
    :doc-author: Trelent
    """
    email = await auth_servise.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.get("/refresh_token", response_model=TokenModel)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
):
    """
    The refresh_token function is used to refresh the access token.
        The function takes in a refresh token and returns an access_token,
        a new refresh_token, and the type of token (bearer).
    
    :param credentials: HTTPAuthorizationCredentials: Get the token from the request header
    :param db: Session: Get the database session, and the credentials: httpauthorizationcredentials parameter is used to get the token from http headers
    :param : Get the user's credentials from the request header
    :return: A dictionary with access_token, refresh_token and token_type
    :doc-author: Trelent
    """
    token = credentials.credentials
    email = await auth_servise.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    access_token = await auth_servise.create_access_token(data={"sub": email})
    refresh_token = await auth_servise.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    The request_email function is used to send an email to the user with a link
    to confirm their account. The function takes in the body of the request, which
    is a RequestEmail object, and uses that information to find out if there is 
    a user with that email address. If there isn't one, then it returns an error message. 
    If there is one, then it sends them an email using FastAPI's background tasks feature.
    
    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url of the server
    :param db: Session: Get the database session
    :param : Get the user's email, username and request
    :return: A dict with a message
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user:
        if user.confirmed:
            return {"message": "Your email is already confirmed"}
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Check your email for confirmation."}
