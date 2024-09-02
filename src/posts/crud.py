import logging
from typing import Optional

from sqlalchemy import desc, select
from sqlalchemy.engine import Result
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.core.config import configure_logging
from src.core.exceptions import ExceptDB, ExceptUser
from src.posts.models import Post
from src.posts.schemas import PostCreate, PostWithAutor, PostInfo
from src.users.models import User

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


async def add_new_post(session: AsyncSession, post: PostCreate, id_user: int) -> None:
    """
        Добавление поста в БД
    :param session: AsyncSession
        сессия БД
    :param post: PostCreate
        пост пользователя
    :param id_user: id_user
        id пользователя
    :return: None
    """
    new_post: Post = Post(**post.model_dump())
    new_post.id_user = id_user
    try:
        session.add(new_post)
        await session.commit()
    except SQLAlchemyError:
        logger.exception("Error add new post")
        raise ExceptDB("Error in DB")


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


async def get_post_with_user_from_db(session: AsyncSession) -> list[PostWithAutor]:
    """
        Возвращает список постов с автором
    :param session: AsyncSession
        сессия ДБ
    :return: list[PostWithAutor]
        Список постов с автором
    """
    stmt = select(Post).options(joinedload(Post.user))
    posts = await session.scalars(stmt)
    lst_posts: list[PostWithAutor] = list()
    for post in posts:  # type: Post
        post_with_author: PostWithAutor = PostWithAutor(
            user=post.user.username,
            title=post.title,
            body=post.body,
            data_create=post.date_creation,
        )
        lst_posts.append(post_with_author)
    return lst_posts


async def add_like_post(session: AsyncSession, id_post: int, id_user: int) -> PostInfo:
    """
        Добавление лайка к посту
    :param session: AsyncSession
        сессия БД
    :param id_post: int
        id поста
    :param id_user: int
        id пользователя
    :return: PostInfo
        информация о лайкнутом посте
    """
    logger.info(
        "Start add like from user with id %d fot post with id %d", id_user, id_post
    )
    user: User = await session.get(User, id_user)

    stmt = select(Post).where(Post.id == id_post).options(selectinload(Post.like_user))
    res: Result = await session.execute(stmt)
    post: Post = res.scalars().first()
    # проверка принадлежности поста пользователю
    if post.id_user == id_user:
        logger.info("Post belongs to the user")
        raise ExceptUser("This user's post")

    user_post: User = await session.get(User, post.id_user)
    try:
        post.like_user.append(user)
        await session.commit()
    except SQLAlchemyError as exp:
        logger.exception(f"Error db {exp}")
        await session.rollback()
        raise ExceptDB("Error in DB")
    else:
        logger.info("Like to post add complete")
        return PostInfo(
            title_post=post.title,
            name_user=user_post.username,
            email=user_post.email,
            name_friend=user.username,
        )


async def delete_like_post_db(session: AsyncSession, id_post: int, id_user: int) -> bool:
    """
        Удаление лайка к посту
    :param session: AsyncSession
        сессия БД
    :param id_post: int
        id поста
    :param id_user: int
        id пользователя
    :return: bool
        результат выполнения
    """
    logger.info(
        "Start delete like from user with id %d fot post with id %d", id_user, id_post
    )
    user: User = await session.get(User, id_user)

    stmt = select(Post).where(Post.id == id_post).options(selectinload(Post.like_user))
    res: Result = await session.execute(stmt)
    post: Post = res.scalars().first()
    # проверка принадлежности поста пользователю
    if post.id_user == id_user:
        logger.info("Post belongs to the user")
        return False
    try:
        post.like_user.remove(user)
        await session.commit()
    except SQLAlchemyError as exp:
        logger.exception(f"Error db {exp}")
        await session.rollback()
        return False
    else:
        logger.info("Like to post delete complete")
        return True
