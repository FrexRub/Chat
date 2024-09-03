from typing import Annotated

from fastapi import APIRouter, Depends, Form, Path, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import templates
from src.core.database import get_async_session
from src.core.exceptions import ExceptDB, ExceptUser
from src.posts.crud import (
    add_like_post,
    add_new_post,
    delete_like_post_db,
    delete_post,
    get_post_from_db,
    get_post_with_user_from_db,
)
from src.posts.models import Post
from src.posts.schemas import PostCreate, PostWithAutor, PostInfo
from src.users.depends import current_active_user
from src.users.models import User
from src.tasks.tasks import send_email

router = APIRouter(prefix="/posts", tags=["Post"])


@router.get("/")
async def get_all_posts(session: AsyncSession = Depends(get_async_session)):
    posts: list[Post] = await get_post_from_db(session)
    return posts


@router.get("/new_post/", name="posts:new_post", response_class=HTMLResponse)
def add_new_post_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="posts/add_post.html",
    )


@router.get("/{id}")
@cache(expire=60)
async def get_posts_user_by_id(
    id: Annotated[int, Path()],
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    posts: list[Post] = await get_post_from_db(session=session, id_user=id)
    return posts


@router.post("/", response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
async def create_new_post(
    request: Request,
    title: str = Form(),
    content: str = Form(),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
) -> HTMLResponse:
    post: PostCreate = PostCreate(title=title, body=content)
    try:
        await add_new_post(session=session, post=post, id_user=user.id)
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
    posts: list[PostWithAutor] = await get_post_with_user_from_db(session=session)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"posts": posts},
    )


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
@cache(expire=60)
async def get_posts_with_user(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    posts: list[PostWithAutor] = await get_post_with_user_from_db(session)
    return posts


@router.post(
    "/{id}/likes",
    status_code=201,
    response_class=JSONResponse,
)
async def post_like_post(
    response: Response,
    id: Annotated[int, Path(gt=0)],
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    try:
        res: PostInfo = await add_like_post(session=session, id_post=id, id_user=user.id)
    except ExceptUser:
        response.status_code = 400
        return {"result": "Error User"}
    except ExceptDB:
        response.status_code = 400
        return {"result": "Error BD"}
    send_email.delay(res.model_dump())
    return {"result": res}


@router.delete(
    "/{id}/likes",
    status_code=200,
    response_class=JSONResponse,
)
async def delete_like_post(
    response: Response,
    id: Annotated[int, Path(gt=0)],
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    res: bool = await delete_like_post_db(session=session, id_post=id, id_user=user.id)
    if not res:
        response.status_code = 400
    return {"result": res}


@router.post("/test")
def post_test(
    title: str = Form(),
    content: str = Form(),
    user: User = Depends(current_active_user),
):
    """
    Тестовый эндпоинт для автотеста
    """
    return {"title": title, "content": content}
