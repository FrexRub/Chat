from typing import Optional
import logging

from sqlalchemy import select, desc
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.posts.models import Post
from src.posts.schemas import PostCreate
from src.core.config import configure_logging
from src.core.exceptions import ExceptDB


configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


async def get_post_from_db(
    session: AsyncSession, id_user: Optional[int] = None
) -> list[Post]:
    """
    Получение постов всех пользователей или пользователя указанного id
    :param session: AsyncSession
        сессия БД
    :param id_user: Optional[int] = None
        id пользователя, по умолчанию не указывается
    :return: list[Post]
        список постов
    """
    if id_user:
        stmt = select(Post).where(Post.id_user == id_user)
    else:
        stmt = select(Post).order_by(desc(Post.id))
    posts = await session.scalars(stmt)
    return list(posts)


async def add_new_post(session: AsyncSession, post: PostCreate, id_user: int) -> int:
    """
        Добавление поста в БД
    :param session: AsyncSession
        сессия БД
    :param post: PostCreate
        пост пользователя
    :param id_user: id_user
        id пользователя
    :return: int
        id нового поста
    """
    new_post: Post = Post(**post.model_dump())
    new_post.id_user = id_user
    try:
        session.add(new_post)
        await session.commit()
    except SQLAlchemyError:
        logger.exception("Error add new post")
        raise ExceptDB("Error in DB")
    return new_post.id


async def delete_post(session: AsyncSession, id_post: int, id_user: int) -> bool:
    """
        Удаление поста пользователя
    :param session: AsyncSession
        сессия БД
    :param id_post: int
        id удаленного поста
    :param id_user: int
        id пользователя
    :return: bool
        статус выполнения операции удаления
    """
    stmt = select(Post).where(Post.id == id_post)
    res = await session.execute(stmt)
    post: Post = res.scalars().first()
    if post.id_user == id_user:
        try:
            await session.delete(post)
            await session.commit()
        except SQLAlchemyError:
            logger.exception("Error delete post")
            raise ExceptDB("Error in DB")
        else:
            return True
    else:
        return False
