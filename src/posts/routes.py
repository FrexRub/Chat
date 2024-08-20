from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.posts.models import Post
from src.posts.schemas import PostCreate, PostRead
from src.posts.crud import get_post_from_db

router = APIRouter(prefix="/posts", tags=["Post"])


@router.get("/")
async def get_all_posts(session: AsyncSession = Depends(get_async_session)):
    posts: list[Post] = await get_post_from_db(session)
    return posts


# @router.post("/", response_class=JSONResponse)
# def create_new_post(
#     post: PostCreate,
#     session: AsyncSession = Depends(get_async_session),
#     user: User = Depends(current_active_user),
# ):
#     pass
