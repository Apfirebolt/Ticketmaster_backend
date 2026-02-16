from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from backend import db
from backend.auth.jwt import get_current_user
from backend.auth.schema import DisplayAccount
from . import schema, services

router = APIRouter(tags=['Chat'], prefix='/api/chat')


@router.post('/send', status_code=status.HTTP_201_CREATED, response_model=schema.MessageResponse)
async def send_message(
    message_data: schema.MessageCreate,
    database: Session = Depends(db.get_db),
    current_user: DisplayAccount = Depends(get_current_user)
):
    """Send a message to another user"""
    message = await services.send_message(database, message_data, current_user.id)
    return message


@router.get('/conversations', response_model=List[schema.ConversationWithParticipants])
async def get_user_conversations(
    database: Session = Depends(db.get_db),
    current_user: DisplayAccount = Depends(get_current_user)
):
    """Get all conversations for the current user"""
    conversations = await services.get_user_conversations(database, current_user.id)
    
    result = []
    for conversation in conversations:
        conversation_details = await services.get_conversation_with_participants(
            database, conversation.id, current_user.id
        )
        result.append(conversation_details)
    
    return result


@router.get('/conversations/{conversation_id}/messages', response_model=List[schema.MessageResponse])
async def get_conversation_messages(
    conversation_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    database: Session = Depends(db.get_db),
    current_user: DisplayAccount = Depends(get_current_user)
):
    """Get messages for a specific conversation"""
    messages = await services.get_conversation_messages(
        database, conversation_id, current_user.id, limit, offset
    )
    return messages


@router.get('/conversations/{conversation_id}', response_model=schema.ConversationWithParticipants)
async def get_conversation_details(
    conversation_id: int,
    database: Session = Depends(db.get_db),
    current_user: DisplayAccount = Depends(get_current_user)
):
    """Get conversation details with participants"""
    conversation = await services.get_conversation_with_participants(
        database, conversation_id, current_user.id
    )
    return conversation


@router.post('/conversations', status_code=status.HTTP_201_CREATED, response_model=schema.ConversationResponse)
async def create_conversation(
    participant_id: int,
    database: Session = Depends(db.get_db),
    current_user: DisplayAccount = Depends(get_current_user)
):
    """Create a new conversation with another user"""
    conversation = await services.create_conversation(
        database, current_user.id, participant_id
    )
    return conversation


@router.patch('/messages/{message_id}/read', response_model=schema.MessageResponse)
async def mark_message_as_read(
    message_id: int,
    database: Session = Depends(db.get_db),
    current_user: DisplayAccount = Depends(get_current_user)
):
    """Mark a message as read"""
    message = await services.mark_message_as_read(database, message_id, current_user.id)
    return message