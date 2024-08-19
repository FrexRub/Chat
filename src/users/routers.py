from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import templates
from src.core.database import get_async_session
from src.users.models import User
from src.users.crud import get_user_from_db, create_user, add_user_to_db
from src.core.exceptions import NotFindUser, ExceptDB

router = APIRouter(prefix="/users", tags=[])


@router.get("/registration", name="users:registration", response_class=HTMLResponse)
def registration_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="users/registration.html",
    )


@router.post("/login", name="users:login", response_class=JSONResponse)
async def login(
    data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    pass


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

