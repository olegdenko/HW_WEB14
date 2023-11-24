from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import TagModel, TagResponse
from src.repository import tags as repository_tags

router = APIRouter(prefix='/tags', tags=["tags"])


@router.get("/", response_model=List[TagResponse])
async def read_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    The read_tags function returns a list of tags.
        ---
        get:
          summary: Returns a list of tags.
          description: Get all the available tags in the database, with pagination support.
          responses:
            &quot;200&quot;:
              description: A JSON array containing tag objects (see below).  Each object has an id and name field, as well as an optional color field if one was specified when creating the tag.  The response also includes a total_count field indicating how many total results there are for this query (which may be more than what is returned in this response).
    
    :param skip: int: Skip the first n tags
    :param limit: int: Limit the number of tags returned
    :param db: Session: Pass the database session to the function
    :return: A list of tags
    :doc-author: Trelent
    """
    tags = await repository_tags.get_tags(skip, limit, db)
    return tags


@router.get("/{tag_id}", response_model=TagResponse)
async def read_tag(tag_id: int, db: Session = Depends(get_db)):
    """
    The read_tag function returns a single tag from the database.
    
    :param tag_id: int: Specify the tag id to be returned
    :param db: Session: Pass the database session to the function
    :return: A tag object, which is a pydantic model
    :doc-author: Trelent
    """
    tag = await repository_tags.get_tag(tag_id, db)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.post("/", response_model=TagResponse)
async def create_tag(body: TagModel, db: Session = Depends(get_db)):
    """
    The create_tag function creates a new tag in the database.
        The function takes a TagModel object as input and returns the newly created tag.
    
    :param body: TagModel: Specify the type of data that will be passed to the function
    :param db: Session: Pass the database session to the repository layer
    :return: A tagmodel object
    :doc-author: Trelent
    """
    return await repository_tags.create_tag(body, db)


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(body: TagModel, tag_id: int, db: Session = Depends(get_db)):
    """
    The update_tag function updates a tag in the database.
        The function takes an id and a body as input, and returns the updated tag.
        If no tag is found with that id, it raises an HTTPException.
    
    :param body: TagModel: Get the data from the request body
    :param tag_id: int: Find the tag in the database
    :param db: Session: Pass the database session to the repository layer
    :return: A tagmodel object
    :doc-author: Trelent
    """
    tag = await repository_tags.update_tag(tag_id, body, db)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.delete("/{tag_id}", response_model=TagResponse)
async def remove_tag(tag_id: int, db: Session = Depends(get_db)):
    """
    The remove_tag function removes a tag from the database.
        Args:
            tag_id (int): The id of the tag to be removed.
            db (Session, optional): SQLAlchemy Session. Defaults to Depends(get_db).
        Returns:
            Tag: The deleted Tag object.
    
    :param tag_id: int: Specify the id of the tag to be deleted
    :param db: Session: Pass the database session to the function
    :return: The tag that was removed
    :doc-author: Trelent
    """
    tag = await repository_tags.remove_tag(tag_id, db)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag
