from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Path, Request, status, Response, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import HTTPException
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
    add_like_post,
    delete_like_post_db,
)
from src.users.depends import current_active_user
from src.users.models import User

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
    posts: list[PostWithAutor] = await get_post_with_user_from_db(session=session)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"posts": posts},
    )
    # return {"id": id}


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
) -> Optional[dict[str, bool]]:
    res: bool = await add_like_post(session=session, id_post=id, id_user=user.id)
    if not res:
        response.status_code = 400
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
