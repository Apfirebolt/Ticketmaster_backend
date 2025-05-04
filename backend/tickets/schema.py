from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class EventBase(BaseModel):
    id: Optional[int]
    name: str
    description: Optional[str]
    start_time: Optional[datetime]
    start_date: Optional[datetime]
    location: Optional[str]

    class Config:
        orm_mode = True
        anystr_strip_whitespace = True


class EventUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    start_time: Optional[datetime]
    start_date: Optional[datetime]
    location: Optional[str]

    class Config:
        orm_mode = True
        anystr_strip_whitespace = True


class EventList(BaseModel):
    id: Optional[int]
    name: str
    description: Optional[str]
    start_time: datetime
    start_date: datetime
    location: Optional[str]

    class Config:
        orm_mode = True
        anystr_strip_whitespace = True


class TicketSchema(BaseModel):
    id: Optional[int]
    name: str
    description: Optional[str]
    start_time: datetime
    start_date: datetime
    location: Optional[str]

    class Config:
        orm_mode = True
        anystr_strip_whitespace = True


class UserSchema(BaseModel):
    username: str
    email: EmailStr

    class Config:
        orm_mode = True
