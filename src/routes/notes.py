from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import NoteModel, NoteUpdate, NoteStatusUpdate, NoteResponse
from src.repository import notes as repository_notes


router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/", response_model=List[NoteResponse])
async def read_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    The read_notes function returns a list of notes.
    
    :param skip: int: Skip the first n notes
    :param limit: int: Limit the number of notes returned
    :param db: Session: Pass the database session to the function
    :return: A list of notes
    :doc-author: Trelent
    """
    notes = await repository_notes.get_notes(skip, limit, db)
    return notes


@router.get("/{note_id}", response_model=NoteResponse)
async def read_note(note_id: int, db: Session = Depends(get_db)):
    """
    The read_note function returns a note with the given id.
    If no such note exists, it raises an HTTP 404 error.
    
    :param note_id: int: Specify the note id in the url path
    :param db: Session: Pass the database session to the repository layer
    :return: A note, which is a model
    :doc-author: Trelent
    """
    note = await repository_notes.get_note(note_id, db)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )
    return note


@router.post("/", response_model=NoteResponse)
async def create_note(body: NoteModel, db: Session = Depends(get_db)):
    """
    The create_note function creates a new note in the database.
        The body of the request should be a JSON object with the following fields:
            - title (string)
            - description (string)
        Returns:
            A NoteModel object representing the newly created note.
    
    :param body: NoteModel: Pass the data to create a new note
    :param db: Session: Pass the database session to the repository layer
    :return: A notemodel object
    :doc-author: Trelent
    """
    return await repository_notes.create_note(body, db)


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(body: NoteUpdate, note_id: int, db: Session = Depends(get_db)):
    note = await repository_notes.update_note(note_id, body, db)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )
    return note


@router.patch("/{note_id}", response_model=NoteResponse)
async def update_status_note(
    body: NoteStatusUpdate, note_id: int, db: Session = Depends(get_db)
):
    """
    The update_status_note function updates the status of a note.
        The function takes in a NoteStatusUpdate object, which contains the new status for the note.
        It also takes in an integer representing the id of the note to be updated.
        Finally, it takes in an optional Session object that represents our database connection.
    
    :param body: NoteStatusUpdate: Get the body of the request
    :param note_id: int: Identify the note to be updated
    :param db: Session: Pass the database session to the repository layer
    :return: The note object
    :doc-author: Trelent
    """
    note = await repository_notes.update_status_note(note_id, body, db)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )
    return note


@router.delete("/{note_id}", response_model=NoteResponse)
async def remove_note(note_id: int, db: Session = Depends(get_db)):
    """
    The remove_note function removes a note from the database.
        Args:
            note_id (int): The id of the note to remove.
            db (Session, optional): SQLAlchemy Session. Defaults to Depends(get_db).
        Returns:
            Note: The removed Note object.
    
    :param note_id: int: Specify the id of the note to be removed
    :param db: Session: Access the database
    :return: The note that was removed
    :doc-author: Trelent
    """
    note = await repository_notes.remove_note(note_id, db)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )
    return note
