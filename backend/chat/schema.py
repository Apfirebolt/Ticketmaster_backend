from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class MessageCreate(BaseModel):
    content: str
    receiver_id: int


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    content: str
    created_at: datetime
    is_read: int

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    participant_1_id: int
    participant_2_id: int


class ConversationResponse(BaseModel):
    id: int
    participant_1_id: int
    participant_2_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationWithMessages(BaseModel):
    id: int
    participant_1_id: int
    participant_2_id: int
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True


class ConversationWithParticipants(BaseModel):
    id: int
    participant_1: dict
    participant_2: dict
    created_at: datetime
    updated_at: datetime
    last_message: Optional[MessageResponse] = None

    class Config:
        from_attributes = True


class MessageUpdate(BaseModel):
    is_read: Optional[int] = None