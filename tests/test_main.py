import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.users.models import User
from src.users.crud import add_user_to_db
from src.core.jwt_utils import create_hash_password, create_jwt
from src.core.config import COOKIE_NAME
from src.core.exceptions import NotFindUser, ExceptDB
from src.posts.schemas import PostCreate
from src.posts.crud import add_new_post

USERNAME = "Srub"
EMAIL = "frexxx@mail.ru"
PASSWORD = "password"


async def test_get_main(client: AsyncClient):
    response = await client.get("/posts")
    assert response.status_code == 307


async def test_create_user(db_session: AsyncSession):
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


async def test_create_user_raises(db_session: AsyncSession):
    hash_password = create_hash_password(PASSWORD).decode()
    user: User = User(
        username=USERNAME,
        email=EMAIL,
        hashed_password=hash_password,
        is_active=True,
        is_superuser=False,
    )

    with pytest.raises(ExceptDB):
        num: int = await add_user_to_db(db_session, user)


def test_create_jwt():
    jwt: str = create_jwt("1")
    assert jwt.count(".") == 2


async def test_create_new_post(client: AsyncClient):
    # В случае успеха в эндпоинте идет переадресация на страницу index.html
    jwt: str = create_jwt("1")
    cookies = {COOKIE_NAME: jwt}
    post = {"title": "Test", "content": "Test post"}
    response = await client.post("/posts", data=post, cookies=cookies)
    assert response.status_code == 307


async def test_endpoint_test(client: AsyncClient):
    post = {"title": "Test", "content": "Test post"}  # Данные для полей формы
    jwt: str = create_jwt("1")
    cookies = {COOKIE_NAME: jwt}  # Генерация куков для авторизации
    response = await client.post("/posts/test", data=post, cookies=cookies)
    assert response.status_code == 200
    assert response.json()["title"] == "Test"


async def test_add_new_post_bd(db_session: AsyncSession):
    post: PostCreate = PostCreate(title="Test", body="Test post")
    id: int = await add_new_post(session=db_session, post=post, id_user=1)
    assert id == 1
