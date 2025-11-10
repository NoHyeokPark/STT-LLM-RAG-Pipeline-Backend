from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from pathlib import Path

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

class TranscriptRequest(BaseModel):
    directory_name: str
    timestamp: datetime  # "YYYY-MM-DD" 형식

class LocalFileAdapter:
    """파일 경로를 UploadFile 객체처럼 보이게 만드는 래퍼 클래스"""
    def __init__(self, path: Path):
        self._path = path
        self.filename = path.name

    async def read(self) -> bytes:
        # 비동기 파일 라이브러리(aiofiles)를 사용하면 더 효율적이지만,
        # 표준 라이브러리만으로도 호환성을 맞출 수 있습니다.
        return self._path.read_bytes()            