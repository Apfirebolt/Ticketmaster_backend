from fastapi import APIRouter, Depends, status, HTTPException, Query, WebSocket
from sqlalchemy.orm import Session
from typing import List

from backend import db
from backend.auth.jwt import get_current_user, verify_token_simple
from backend.auth.schema import DisplayAccount
from backend.auth.models import User
from . import schema, services
from .websocket import websocket_endpoint

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


@router.websocket("/ws/{user_id}")
async def chat_websocket(
    websocket: WebSocket, 
    user_id: int,
    token: str = Query(...),
    database: Session = Depends(db.get_db)
):
    """WebSocket endpoint for real-time chat"""
    # Verify token
    try:
        token_data = verify_token_simple(token)
        if not token_data:
            await websocket.close(code=4001, reason="Authentication failed")
            return
            
        user = database.query(User).filter(User.email == token_data.email).first()
        if not user or user.id != user_id:
            await websocket.close(code=4001, reason="Authentication failed")
            return
            
        await websocket_endpoint(websocket, user_id)
        
    except Exception as e:
        await websocket.close(code=4001, reason="Authentication failed")