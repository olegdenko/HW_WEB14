from typing import List

from sqlalchemy.orm import Session

from src.database.models import Tag
from src.schemas import TagModel


async def get_tags(skip: int, limit: int, db: Session) -> List[Tag]:
    """
    The get_tags function returns a list of tags from the database.
    
    :param skip: int: Skip a number of rows in the database
    :param limit: int: Limit the number of tags returned
    :param db: Session: Pass the database session to the function
    :return: A list of tags
    :doc-author: Trelent
    """
    return db.query(Tag).offset(skip).limit(limit).all()


async def get_tag(tag_id: int, db: Session) -> Tag:
    """
    The get_tag function returns a Tag object from the database.
        
    
    :param tag_id: int: Specify the id of the tag to be retrieved
    :param db: Session: Pass the database session to the function
    :return: A tag object
    :doc-author: Trelent
    """
    return db.query(Tag).filter(Tag.id == tag_id).first()


async def create_tag(body: TagModel, db: Session) -> Tag:
    """
    The create_tag function creates a new tag in the database.
    
    The create_tag function takes a TagModel object as input and returns a Tag object.
    
    
    :param body: TagModel: Get the name of the tag from the request body
    :param db: Session: Pass the database session to the function
    :return: A tag object
    :doc-author: Trelent
    """
    tag = Tag(name=body.name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


async def update_tag(tag_id: int, body: TagModel, db: Session) -> Tag | None:
    """
    The update_tag function updates a tag in the database.
        Args:
            tag_id (int): The id of the tag to update.
            body (TagModel): The updated TagModel object with new values for name and description.
            db (Session): A Session instance used to query the database.
        Returns:
            Tag | None: If successful, returns an updated Tag object; otherwise, returns None.
    
    :param tag_id: int: Identify which tag to update
    :param body: TagModel: Pass the new tag name to the function
    :param db: Session: Pass the database session to the function
    :return: The updated tag
    :doc-author: Trelent
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        tag .name = body.name
        db.commit()
    return tag


async def remove_tag(tag_id: int, db: Session) -> Tag | None:
    """
    The remove_tag function removes a tag from the database.
        Args:
            tag_id (int): The id of the tag to be removed.
            db (Session): A connection to the database.
        Returns:
            Tag | None: The deleted Tag object or None if no such object exists.
    
    :param tag_id: int: Identify the tag to be deleted
    :param db: Session: Pass the database session to the function
    :return: The tag that was removed from the database
    :doc-author: Trelent
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        db.delete(tag)
        db.commit()
    return tag
