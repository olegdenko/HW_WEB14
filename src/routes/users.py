import hashlib
import cloudinary
import cloudinary.uploader

from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_servise
from src.services.cloud_image import CloudImage
from src.conf.config import settings
from src.schemas import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(auth_servise.get_current_user)):
    """
    The read_users_me function returns the current user's information.
    
    :param current_user: User: Get the current user
    :return: The current user object
    :doc-author: Trelent
    """
    return current_user


@router.patch('/avatar', response_model=UserResponse)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_servise.get_current_user),
                             db: Session = Depends(get_db)):
    """
    The update_avatar_user function updates the avatar of a user.
        Args:
            file (UploadFile): The file to upload.
            current_user (User): The currently logged in user, which is passed by the auth_servise dependency.
            db (Session): A database session instance, which is passed by the get_db dependency.
    
    :param file: UploadFile: Get the file from the request body
    :param current_user: User: Get the current user
    :param db: Session: Access the database
    :return: A user
    :doc-author: Trelent
    """
    public_id = CloudImage.generate_folder_name(current_user.email)

    r = CloudImage.upload(file.file, public_id)
    src_url = CloudImage.get_url_for_avatar(public_id, r)
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user
