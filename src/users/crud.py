from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.engine import Result

from src.users.models import User


async def get_user_from_db(session: AsyncSession, email: str):
    stmt = select(User).where(User.email)
    res: Result = await session.execute(stmt)
    user: Optional[User] = res.scalars().one_or_none()
