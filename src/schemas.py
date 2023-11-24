from datetime import datetime
from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from fastapi import UploadFile

from src.database.models import Role


class UserModel(BaseModel):
    username: str = Field(min_length=3, max_length=12)
    email: EmailStr
    password: str = Field(min_length=6, max_length=8)
    roles: Role
    avatar: Optional[UploadFile] = None


class DateModel(BaseModel):
    date: date

    def json_schema(self):
        """
        The json_schema function is used to generate a JSON schema for the validator.
        The default implementation of this function will return a schema that describes
        the validator as an object with one property, &quot;validate&quot;, which is itself an object
        with two properties: &quot;type&quot; and &quot;description&quot;. The type will be set to either 
        &quot;PlainValidatorFunctionSchema&quot; or &quot;AsyncValidatorFunctionSchema&quot;, depending on whether the 
        validate method returns a value synchronously or asynchronously. The description will be set to the docstring of the validate method. If you want your validators' schemas to
        
        :param self: Represent the instance of the class
        :return: The schema for the validator
        :doc-author: Trelent
        """
        schema = super().json_schema()
        if "PlainValidatorFunctionSchema" in schema.get("type", ""):
            schema = None
        return schema


class TagModel(BaseModel):
    name: str = Field(max_length=25)


class TagResponse(TagModel):
    id: int

    class Config:
        from_attributes = True


class NoteBase(BaseModel):
    title: str = Field(max_length=50)
    description: str = Field(max_length=150)


class ContactBase(BaseModel):
    name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    e_mail: EmailStr
    phone_number: str = Field(max_length=20)
    born_date: DateModel
    description: str = Field(max_length=150)


class NoteModel(NoteBase):
    tags: List[int]


class ContactModel(ContactBase):
    born_date: date


class NoteUpdate(NoteModel):
    done: bool


class ContactUpdate(ContactModel):
    done: bool


class NoteStatusUpdate(BaseModel):
    done: bool


class ContactStatusUpdate(BaseModel):
    done: bool


class NoteResponse(NoteBase):
    id: int
    created_at: datetime
    tags: List[TagResponse]

    class Config:
        from_attributes = True


class ContactResponse(ContactBase):
    id: int
    name: str
    last_name: str
    e_mail: str
    phone_number: str
    born_date: date
    description: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    avatar: str
    roles: Role

    class Config:
        from_attributes = True


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr
