from pydantic import BaseModel, Field
from typing import Optional

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