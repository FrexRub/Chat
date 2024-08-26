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
from src.core.jwt_utils import validate_password, encode_jwt, set_cookie
from src.users.depends import current_active_user

router = APIRouter(prefix="/users", tags=["User"])


@router.get("/registration", name="users:registration", response_class=HTMLResponse)
def registration_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="users/registration.html",
    )


@router.get("/logout", name="users:disconnect", response_class=HTMLResponse)
def logout(response: Response, request: Request):
    response: Response = templates.TemplateResponse(
        request=request,
        name="index.html",
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

    payload = dict()
    payload["sub"] = str(user.id)
    expire = datetime.now(timezone.utc) + timedelta(seconds=900)
    payload["exp"] = expire
    access_token = encode_jwt(payload)

    # resp = RedirectResponse(
    #     url="/users/protected-route", status_code=status.HTTP_302_FOUND
    # )
    resp: Response = templates.TemplateResponse(
        request=request,
        name="index.html",
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
