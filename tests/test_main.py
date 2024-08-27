from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def test_get_main(client: AsyncClient):
    response = await client.get("/posts")
    assert response.status_code == 307
