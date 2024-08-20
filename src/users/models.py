from typing import Optional, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import DateTime, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.posts.models import Post


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[Optional[str]]
    email: Mapped[str] = mapped_column(unique=True, index=True)
    registered_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=datetime.utcnow(),
    )
    hashed_password: Mapped[str]
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    posts: Mapped[list["Post"]] = relationship(back_populates="user")
