from typing import Annotated

from fastapi import APIRouter, Depends, Path, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.core.config import templates
from src.core.exceptions import ExceptDB
from src.posts.models import Post
from src.posts.schemas import PostCreate, PostWithAutor
from src.posts.crud import (
    get_post_from_db,
    add_new_post,
    delete_post,
    get_post_with_user_from_db,
)
from src.users.depends import current_active_user
from src.users.models import User

router = APIRouter(prefix="/posts", tags=["Post"])


@router.get("/")
async def get_all_posts(session: AsyncSession = Depends(get_async_session)):
    posts: list[Post] = await get_post_from_db(session)
    return posts


@router.get("/{id}")
async def get_posts_user_by_id(
    id: Annotated[int, Path()],
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    posts: list[Post] = await get_post_from_db(session=session, id_user=id)
    return posts


@router.post("/", response_class=JSONResponse, status_code=status.HTTP_201_CREATED)
async def create_new_post(
    request: Request,
    post: PostCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    try:
        id: int = await add_new_post(session=session, post=post, id_user=user.id)
    except ExceptDB:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "title_error": "Проблема c добавлением поста",
                "text_error": "Ошибка в БД",
            },
            status_code=404,
        )
    return {"id": id}


@router.delete("/{id}", response_class=JSONResponse)
async def delete_post_by_id(
    id: Annotated[int, Path()],
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    try:
        res: bool = await delete_post(session=session, id_post=id, id_user=user.id)
    except ExceptDB:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "title_error": "Проблема c удалением поста",
                "text_error": "Ошибка в БД",
            },
            status_code=404,
        )
    return bool(res)


@router.get("/users/", response_class=JSONResponse)
async def get_posts_with_user(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    posts: list[PostWithAutor] = await get_post_with_user_from_db(session)
    return posts
