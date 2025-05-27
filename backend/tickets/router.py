from typing import List
from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from backend.auth.jwt import get_current_user
from backend.auth.models import User

from backend import db

from . import schema
from . import services


router = APIRouter(tags=["Event"], prefix="/api/events")


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.EventBase)
async def create_new_event(
    request: schema.EventBase,
    database: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    user = database.query(User).filter(User.email == current_user.email).first()
    result = await services.create_new_event(request, database, user)
    return result


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schema.EventList])
async def event_list(
    database: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    result = await services.get_event_listing(database, current_user.id)
    return result


@router.get(
    "/{event_id}", status_code=status.HTTP_200_OK, response_model=schema.EventBase
)
async def get_event_by_id(
    event_id: int,
    database: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    return await services.get_event_by_id(event_id, current_user.id, database)


@router.delete(
    "/{event_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response
)
async def delete_event_by_id(
    event_id: str,
    database: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    return await services.delete_event_by_id(event_id, current_user, database)


@router.put(
    "/{event_id}", status_code=status.HTTP_200_OK, response_model=schema.EventBase
)
async def update_event_by_id(
    event_id: int,
    request: schema.EventUpdate,
    database: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    return await services.update_event_by_id(event_id, request, current_user, database)
