import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import configure_logging
from src.core.exceptions import ExceptDB, NotFindUser
from src.core.jwt_utils import create_hash_password
from src.users.models import User

configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


async def get_user_from_db(session: AsyncSession, email: str) -> User:
    logger.info("Start find user by email: %s", email)
    stmt = select(User).where(User.email == email)
    res: Result = await session.execute(stmt)
    user: Optional[User] = res.scalars().one_or_none()
    if not user:
        logger.info("User not find")
        raise NotFindUser(f"Not find user by email {email}")
    logger.info("User has benn found")
    return user


async def get_user_by_id(session: AsyncSession, id_user: int) -> User:
    logger.info("Start find user by id %s", id_user)
    stmt = select(User).where(User.id == id_user)
    res: Result = await session.execute(stmt)
    user: User = res.scalars().first()
    logger.info("User by id %s", user.email)
    return user


def create_user(username: str, email: str, password: str) -> User:
    logger.info("Start create user with email %s", email)
    hash_password = create_hash_password(password).decode()
    user: User = User(
        username=username,
        email=email,
        hashed_password=hash_password,
        is_active=True,
        is_superuser=False,
    )
    return user


async def add_user_to_db(session: AsyncSession, user: User) -> int:
    logger.info("Start add new user")
    try:
        session.add(user)
        await session.commit()
    except SQLAlchemyError as exc:
        logger.exception(exc)
        await session.rollback()
        raise ExceptDB("Error in DB")
    else:
        logger.info("User add in db")
        return user.id

    # try:
    #     id: int = await add_user_to_db(session=session, user=user)
    # except ExceptDB as exc:
    #     # raise HTTPException(
    #     #         status_code=status.HTTP_401_UNAUTHORIZED,
    #     #         detail=f"invalid add user in DB: {exc}"
    #     #     )
    #     return templates.TemplateResponse(
    #         request=request,
    #         name="error.html",
    #         context={
    #             "title_error": "Проблема при регистрации клиента",
    #             "text_error": "Ошибка записи БД, попробуйте попозже",
    #         },
    #     )
    # else:
    #     return id
