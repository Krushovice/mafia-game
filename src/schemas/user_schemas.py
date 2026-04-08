from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    telegram_id: int
    username: Optional[str] = None


class UserRead(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str]

    class Config:
        orm_mode = True


class UserResourceRead(BaseModel):
    id: int
    user_id: int
    money: int
    influence: int
    wanted_level: int

    class Config:
        orm_mode = True
