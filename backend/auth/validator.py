from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from . models import User


async def verify_email_exist(email: str, db_session: Session) -> Optional[User]:
    return db_session.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()
