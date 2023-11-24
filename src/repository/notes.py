from typing import List

from sqlalchemy.orm import Session

from src.database.models import Note, Tag
from src.schemas import NoteModel, NoteUpdate, NoteStatusUpdate


async def get_notes(skip: int, limit: int, db: Session) -> List[Note]:
    """
    The get_notes function returns a list of notes from the database.
    
    :param skip: int: Skip a number of notes in the database
    :param limit: int: Limit the number of notes returned
    :param db: Session: Pass the database session to the function
    :return: A list of note objects
    :doc-author: Trelent
    """
    return db.query(Note).offset(skip).limit(limit).all()


async def get_note(note_id: int, db: Session) -> Note:
    """
    The get_note function returns a note from the database based on its id.
        
    
    :param note_id: int: Get the note from the database
    :param db: Session: Pass the database session to the function
    :return: A note object
    :doc-author: Trelent
    """
    return db.query(Note).filter(Note.id == note_id).first()


async def create_note(body: NoteModel, db: Session) -> Note:
    """
    The create_note function creates a new note in the database.
        It takes a NoteModel object as input and returns the newly created Note object.
    
    
    :param body: NoteModel: Get the data from the request body
    :param db: Session: Pass the database session to the function
    :return: A note object
    :doc-author: Trelent
    """
    tags = db.query(Tag).filter(Tag.id.in_(body.tags)).all()
    note = Note(title=body.title, description=body.description, tags=tags)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


async def remove_note(note_id: int, db: Session) -> Note | None:
    """
    The remove_note function removes a note from the database.
        
    
    :param note_id: int: Specify the id of the note to be removed
    :param db: Session: Pass the database session to the function
    :return: The note that was removed
    :doc-author: Trelent
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if note:
        db.delete(note)
        db.commit()
    return note


async def update_note(note_id: int, body: NoteUpdate, db: Session) -> Note | None:
    """
    The update_note function updates a note in the database.
        
    
    :param note_id: int: Identify the note to update
    :param body: NoteUpdate: Get the data from the request body
    :param db: Session: Connect to the database
    :return: A note object
    :doc-author: Trelent
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if note:
        tags = db.query(Tag).filter(Tag.id.in_(body.tags)).all()
        note.title = body.title
        note.description = body.description
        note.done = body.done
        note.tags = tags
        db.commit()
    return note


async def update_status_note(note_id: int, body: NoteStatusUpdate, db: Session) -> Note | None:
    """
    The update_status_note function updates the status of a note in the database.
        
    
    :param note_id: int: Identify the note to be updated
    :param body: NoteStatusUpdate: Get the data from the request body
    :param db: Session: Access the database
    :return: A note object, but the return type is none
    :doc-author: Trelent
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if note:
        note.done = body.done
        db.commit()
    return note
