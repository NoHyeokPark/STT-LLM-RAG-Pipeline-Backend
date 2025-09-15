from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserModel(BaseModel):
    name: str = Field(...)
    id: str = Field(...)
    pw: str = Field(...) # 1~5년차

    class Config:
        schema_extra = {
            "example": {
                "name": "John Doe",
                "id": "Computer",
                "pw": "2434"
            }
        }

class UpdateUserModel(BaseModel):
    name: Optional[str]
    id: Optional[str]
    pw: Optional[str]

class PasswordUpdate(BaseModel):
    old_password: str = Field(...)
    new_password: str = Field(...)
    class Config:
        schema_extra = {
            "example": {
                "old_password": "John Doe",
                "inew_password": "Computer"
            }
        }

class htmlModel(BaseModel):
    title: str = Field(...)
    content: str = Field(...)
    uploadedAt: datetime = Field(...)
    participants: list[str] = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "title": "Sample HTML Document",
                "content": "<html><body>" + "<div>This is a large file.</div>" * 1000 + "</body></html>",
                "uploadedAt": "2025-01-01 00:00:00",
                "participants": ["asd@mail.com", "zxc@mail.com", "qwe@mail.com"]
            }
        }
        