import logging
from typing import AsyncIterator

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from sqlalchemy.ext.asyncio import AsyncSession
import uvicorn
from contextlib import asynccontextmanager
from redis import asyncio as aioredis


from src.core.config import configure_logging, templates
from src.core.database import get_async_session
from src.users.routers import router as router_users
from src.posts.routes import router as router_posts
from src.posts.schemas import PostWithAutor
from src.posts.crud import get_post_with_user_from_db

configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


app = FastAPI(lifespan=lifespan)


origins = [
    "http://localhost:8000",
]

# include config CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
    ],
)


app.include_router(router_users)
app.include_router(router_posts)


@app.get("/", name="main:index", response_class=HTMLResponse)
async def main_index(
    request: Request, session: AsyncSession = Depends(get_async_session)
) -> HTMLResponse:
    posts: list[PostWithAutor] = await get_post_with_user_from_db(session=session)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"posts": posts},
    )


if __name__ == "__main__":
    uvicorn.run("main:app")
