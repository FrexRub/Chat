from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (DateTime, ForeignKey, String, Text, UniqueConstraint,
                        func, select)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, object_session, relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.users.models import User


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), default="", server_default="")
    body: Mapped[str] = mapped_column(Text, default="", server_default="")
    date_creation: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=datetime.utcnow(),
    )
    id_user: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(back_populates="posts")
    like_user: Mapped[list["User"]] = relationship(
        secondary="likes_post",
        back_populates="like_post",
        uselist=True,
    )

    @hybrid_property
    def like_count(self):
        query = select(func.count(LikesPost.post_id)).where(
            LikesPost.post_id == self.id
        )
        result = object_session(self).execute(query)
        return result.scalars().one()

    @like_count.expression
    def like_count(cls):
        return (
            select(func.count(LikesPost.post_id))
            .where(LikesPost.post_id == cls.id)
            .label("like_count")
        )

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, title={self.title!r}, user_id={self.user_id})"

    def __repr__(self):
        return str(self)


class LikesPost(Base):
    __tablename__ = "likes_post"
    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="idx_unique_user_tweet"),
    )

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    # user: Mapped["User"] = relationship(back_populates="user_details")
    # product: Mapped["Product"] = relationship(back_populates="orders_details")
