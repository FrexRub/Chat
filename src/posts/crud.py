from typing import Optional

from sqlalchemy import select, desc
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from src.posts.models import Post


async def get_post_from_db(
    session: AsyncSession, id_user: Optional[int] = None
) -> list[Post]:
    if id_user:
        stmt = select(Post).where(Post.id_user == id_user)
    else:
        stmt = select(Post).order_by(desc(Post.id))
    # res: Result = await session.execute(stmt)
    posts = await session.scalars(stmt)
    return list(posts)


# async def_
