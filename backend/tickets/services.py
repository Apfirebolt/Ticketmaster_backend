from fastapi import HTTPException, status
from typing import List
from . import models
from backend.auth.models import User
from datetime import datetime
from sqlalchemy.orm import Session
from pydantic import HttpUrl


async def create_new_event(
    request, database: Session, current_user: User
) -> models.Event:
    try:
        # Check if request.poster is an HttpUrl object and convert to string if so
        poster_str = (
            str(request.poster)
            if isinstance(request.poster, HttpUrl)
            else request.poster
        )

        # error if the same event has been added by the same user
        existing_event = (
            database.query(models.Event)
            .filter(
                models.Event.eventID == request.eventID,
                models.Event.owner_id == current_user.id,
            )
            .first()
        )
        if existing_event:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event already exists in your collection.",
            )

        new_event = models.Event(
            title=request.title,
            eventID=request.eventID,
            poster=poster_str,  # Use the converted string
            date=request.date,
            location=request.location,
            owner_id=current_user.id,
            createdDate=datetime.now(),
        )
        database.add(new_event)
        database.commit()
        database.refresh(new_event)
        return new_event
    except Exception as e:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the event: {str(e)}",
        )


async def get_event_listing(database, current_user) -> List[models.Event]:
    try:
        events = (
            database.query(models.Event)
            .filter(models.Event.owner_id == current_user)
            .all()
        )
        return events
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching events: {str(e)}",
        )


async def get_event_by_id(event_id, current_user, database):
    try:
        event = (
            database.query(models.Event)
            .filter_by(id=event_id, owner_id=current_user)
            .first()
        )
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Event Not Found!"
            )
        return event
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the event: {str(e)}",
        )


async def delete_event_by_id(event_id, current_user: User, database: Session):
    try:
        # check if event belongs to the user
        event = (
            database.query(models.Event)
            .filter_by(id=event_id, owner_id=current_user.id)
            .first()
        )
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Event Not Found!"
            )
        database.query(models.Event).filter(models.Event.eventID == event_id).delete()
        database.commit()
    except Exception as e:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the event: {str(e)}",
        )
