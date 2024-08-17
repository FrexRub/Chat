from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import templates
from src.core.database import get_async_session
from src.users.models import User

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
    find_user: User = await get_user_from_db(name=email, session=session)
    if find_user:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "title_error": "Проблема при регистрации клиента",
                "text_error": "Клиент с данным email уже существует",
            },
        )
    hash_password = create_hash_password(password).decode()
    user: User = User(
        user=username,
        email=email,
        hashed_password=hash_password,
        is_active=True,
        is_superuser=False,
        is_verified=False,
    )
    try:
        id: int = await add_user_to_db(session=session, user=user)
    except ExceptDB as exc:
        # raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail=f"invalid add user in DB: {exc}"
        #     )
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
