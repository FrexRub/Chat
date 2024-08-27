from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.users.crud import create_user
from src.users.models import User
from src.users.crud import add_user_to_db
from src.core.jwt_utils import create_hash_password

USERNAME = "Srub"
EMAIL = "frexxx@mail.ru"
PASSWORD = "password"


async def test_get_main(client: AsyncClient):
    response = await client.get("/posts")
    assert response.status_code == 307


async def test_create_user(db_session):
    hash_password = create_hash_password(PASSWORD).decode()
    user: User = User(
        username=USERNAME,
        email=EMAIL,
        hashed_password=hash_password,
        is_active=True,
        is_superuser=False,
    )
    assert user.username == USERNAME
    num: int = await add_user_to_db(db_session, user)
    assert num == 1
