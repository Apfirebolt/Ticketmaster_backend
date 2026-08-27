from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, or_, select
from fastapi import HTTPException, status
from typing import Any, List, Optional
from datetime import datetime

from . import models, schema
from ..auth.models import User


async def create_conversation(db: Session, participant_1_id: int, participant_2_id: int) -> models.Conversation:
    """Create a new conversation between two users"""
    if participant_1_id == participant_2_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create conversation with yourself"
        )
    
    # Check if conversation already exists between these two users
    existing_conversation = db.execute(
        select(models.Conversation).where(
            or_(
                and_(models.Conversation.participant_1_id == participant_1_id,
                     models.Conversation.participant_2_id == participant_2_id),
                and_(models.Conversation.participant_1_id == participant_2_id,
                     models.Conversation.participant_2_id == participant_1_id),
            )
        )
    ).scalar_one_or_none()
    
    if existing_conversation:
        return existing_conversation
    
    # Verify both users exist
    user1 = db.execute(
        select(User).where(User.id == participant_1_id)
    ).scalar_one_or_none()
    user2 = db.execute(
        select(User).where(User.id == participant_2_id)
    ).scalar_one_or_none()
    
    if not user1 or not user2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both users not found"
        )
    
    db_conversation = models.Conversation(
        participant_1_id=participant_1_id,
        participant_2_id=participant_2_id
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation


async def send_message(db: Session, message_data: schema.MessageCreate, sender_id: int) -> models.Message:
    """Send a message in a conversation"""
    # Find or create conversation
    conversation = await create_conversation(db, sender_id, message_data.receiver_id)
    
    db_message = models.Message(
        conversation_id=conversation.id,
        sender_id=sender_id,
        content=message_data.content
    )
    
    db.add(db_message)
    
    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_message)
    return db_message


async def get_user_conversations(db: Session, user_id: int) -> List[models.Conversation]:
    """Get all conversations for a user"""
    conversations = db.execute(
        select(models.Conversation)
        .where(
            or_(
                models.Conversation.participant_1_id == user_id,
                models.Conversation.participant_2_id == user_id,
            )
        )
        .order_by(desc(models.Conversation.updated_at))
    ).scalars().all()
    
    return conversations


async def get_conversation_messages(db: Session, conversation_id: int, user_id: int, limit: int = 50, offset: int = 0) -> List[models.Message]:
    """Get messages for a specific conversation"""
    # Verify user is part of the conversation
    conversation = db.execute(
        select(models.Conversation).where(
            models.Conversation.id == conversation_id,
            or_(
                models.Conversation.participant_1_id == user_id,
                models.Conversation.participant_2_id == user_id,
            ),
        )
    ).scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or access denied"
        )
    
    messages = db.execute(
        select(models.Message)
        .where(models.Message.conversation_id == conversation_id)
        .order_by(desc(models.Message.created_at))
        .offset(offset)
        .limit(limit)
    ).scalars().all()
    
    return messages


async def mark_message_as_read(db: Session, message_id: int, user_id: int) -> models.Message:
    """Mark a message as read"""
    message = db.execute(
        select(models.Message).where(models.Message.id == message_id)
    ).scalar_one_or_none()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Verify user is part of the conversation and not the sender
    conversation = db.execute(
        select(models.Conversation).where(
            models.Conversation.id == message.conversation_id,
            or_(
                models.Conversation.participant_1_id == user_id,
                models.Conversation.participant_2_id == user_id,
            ),
        )
    ).scalar_one_or_none()
    
    if not conversation or message.sender_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot mark own message as read or access denied"
        )
    
    message.is_read = 1
    db.commit()
    db.refresh(message)
    return message


async def get_conversation_with_participants(db: Session, conversation_id: int, user_id: int) -> dict[str, Any]:
    """Get conversation details with participant information"""
    conversation = db.execute(
        select(models.Conversation).where(
            models.Conversation.id == conversation_id,
            or_(
                models.Conversation.participant_1_id == user_id,
                models.Conversation.participant_2_id == user_id,
            ),
        )
    ).scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or access denied"
        )
    
    # Get the last message
    last_message = db.execute(
        select(models.Message)
        .where(models.Message.conversation_id == conversation_id)
        .order_by(desc(models.Message.created_at))
    ).scalar_one_or_none()
    
    # Get participant details
    participant_1 = db.execute(
        select(User).where(User.id == conversation.participant_1_id)
    ).scalar_one_or_none()
    participant_2 = db.execute(
        select(User).where(User.id == conversation.participant_2_id)
    ).scalar_one_or_none()
    
    return {
        "id": conversation.id,
        "participant_1": {
            "id": participant_1.id,
            "username": participant_1.username,
            "email": participant_1.email
        },
        "participant_2": {
            "id": participant_2.id,
            "username": participant_2.username,
            "email": participant_2.email
        },
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "last_message": last_message
    }