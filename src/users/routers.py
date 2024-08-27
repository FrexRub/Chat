from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Request, Depends, Form, status, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import templates, COOKIE_NAME
from src.core.database import get_async_session
from src.users.models import User
from src.users.crud import get_user_from_db, create_user, add_user_to_db
from src.core.exceptions import NotFindUser, ExceptDB
from src.core.jwt_utils import validate_password, encode_jwt, set_cookie, create_jwt
from src.users.depends import current_active_user
from src.posts.schemas import PostWithAutor
from src.posts.crud import get_post_with_user_from_db

router = APIRouter(prefix="/users", tags=["User"])


@router.get("/registration", name="users:registration", response_class=HTMLResponse)
def registration_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="users/registration.html",
    )


@router.get("/logout", name="users:disconnect", response_class=HTMLResponse)
async def logout(
    response: Response,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    posts: list[PostWithAutor] = await get_post_with_user_from_db(session=session)
    response: Response = templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"posts": posts},
    )
    response.delete_cookie(COOKIE_NAME)
    return response


@router.post("/login", name="users:login", response_class=JSONResponse)
async def login(
    request: Request,
    data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    username = data.username
    password = data.password
    try:
        user: User = await get_user_from_db(email=username, session=session)
    except NotFindUser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User {username} not found",
        )

    if not validate_password(
        password=password,
        hashed_password=user.hashed_password.encode(),
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error password for login: {username}",
        )

    access_token: str = create_jwt(str(user.id))

    posts: list[PostWithAutor] = await get_post_with_user_from_db(session=session)
    resp: Response = templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"posts": posts},
        status_code=status.HTTP_302_FOUND,
    )
    set_cookie(resp, access_token)
    return resp


@router.post("/regdata", response_class=JSONResponse)
async def regdata(
    request: Request,
    username=Form(),
    email=Form(),
    password=Form(),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        find_user: User = await get_user_from_db(email=email, session=session)
    except NotFindUser:
        user: User = create_user(username, email, password)
    else:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "title_error": "Проблема при регистрации клиента",
                "text_error": "Клиент с данным email уже существует",
            },
        )

    try:
        id: int = await add_user_to_db(session=session, user=user)
    except ExceptDB:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "title_error": "Проблема при регистрации клиента",
                "text_error": "Ошибка записи БД, попробуйте попозже",
            },
        )
    else:
        return {"id": id}


@router.get("/protected-route")
async def protected_route(user: User = Depends(current_active_user)):
    return f"Hello, USer {user.email}"
