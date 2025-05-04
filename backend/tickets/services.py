from fastapi import HTTPException, status
from typing import List
from . import models
from backend.auth.models import User
from sqlalchemy.orm import Session


async def create_new_event(
    request, database: Session, current_user: User
) -> models.Event:
    try:
        # error if the same event has been added by the same user
        existing_event = (
            database.query(models.Event)
            .filter(
                models.Event.name == request.name,
                models.Event.user_id == current_user.id,
            )
            .first()
        )
        if existing_event:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event already exists in your collection.",
            )

        new_event = models.Event(
            name=request.name,
            description=request.description,
            start_date=request.start_date,
            start_time=request.start_time,
            location=request.location,
            user_id=current_user.id,
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
            .filter(models.Event.user_id == current_user)
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
            .filter_by(id=event_id, user_id=current_user)
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
    

async def update_event_by_id(
    event_id, request, current_user: User, database: Session
) -> models.Event:
    try:
        # check if event belongs to the user
        event = (
            database.query(models.Event)
            .filter_by(id=event_id, user_id=current_user.id)
            .first()
        )
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Event Not Found!"
            )

        # update event details
        event.name = request.name
        event.description = request.description
        event.start_date = request.start_date
        event.start_time = request.start_time
        event.location = request.location

        database.commit()
        database.refresh(event)
        return event
    except Exception as e:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the event: {str(e)}",
        )


async def delete_event_by_id(event_id, current_user: User, database: Session):
    try:
        # check if event belongs to the user
        event = (
            database.query(models.Event)
            .filter_by(id=event_id, user_id=current_user.id)
            .first()
        )
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Event Not Found!"
            )
        database.query(models.Event).filter(models.Event.id == event_id).delete()
        database.commit()
    except Exception as e:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the event: {str(e)}",
        )
