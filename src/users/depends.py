from fastapi import Depends, status
from fastapi.security import APIKeyCookie, APIKeyHeader
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import COOKIE_NAME
from src.core.jwt_utils import decode_jwt
from src.users.models import User
from src.core.database import get_async_session
from src.users.crud import get_user_by_id

cookie_scheme = APIKeyCookie(name=COOKIE_NAME)
header_scheme = APIKeyHeader(
    name="x-key"
)  # используется в случаи наличия токена в заголовке


async def current_active_user(
    token: str = Depends(cookie_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized"
        )
    payload = decode_jwt(token)
    id_user: int = int(payload["sub"])
    user: User = await get_user_by_id(session=session, id_user=id_user)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not activate"
        )
    return user
