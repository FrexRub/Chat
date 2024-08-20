from typing import Optional

from sqlalchemy import select, desc
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from src.posts.models import Post
from src.posts.schemas import PostCreate


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


async def add_new_post(session: AsyncSession, post: PostCreate, id_user: int) -> int:
    new_post: Post = Post(**post.model_dump())
    new_post.id_user = id_user
    session.add(new_post)
    await session.commit()
    return new_post.id


async def delete_post(session: AsyncSession, id_post: int, id_user: int) -> bool:
    stmt = select(Post).where(Post.id == id_post)
    res = await session.execute(stmt)
    post: Post = res.scalars().first()
    if post.id_user == id_user:
        await session.delete(post)
        await session.commit()
        return True
    else:
        return False
