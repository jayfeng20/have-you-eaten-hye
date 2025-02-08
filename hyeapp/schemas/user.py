from pydantic import BaseModel, EmailStr, constr
from typing import Optional


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserProfile(UserBase):
    nickname: Optional[str] = None

    class Config:
        from_attributes = True


class NicknameUpdate(BaseModel):
    nickname: constr(min_length=1, max_length=50)
