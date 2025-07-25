from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class EventBase(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    start_date: Optional[datetime] = None
    location: Optional[str] = None

    class Config:
        from_attributes = True
        str_strip_whitespace = True


class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    start_date: Optional[datetime] = None
    location: Optional[str] = None

    class Config:
        from_attributes = True
        str_strip_whitespace = True


class EventList(BaseModel):
    id: Optional[int] 
    name: str
    description: Optional[str]
    start_time: datetime
    start_date: datetime
    location: Optional[str]

    class Config:
        from_attributes = True
        str_strip_whitespace = True


class TicketSchema(BaseModel):
    id: Optional[int]
    name: str
    description: Optional[str]
    start_time: str
    start_date: str
    location: Optional[str]

    class Config:
        from_attributes = True
        str_strip_whitespace = True


class UserSchema(BaseModel):
    username: str
    email: EmailStr

    class Config:
        from_attributes = True
