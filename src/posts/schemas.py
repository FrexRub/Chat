from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PostCreate(BaseModel):
    title: str
    body: str


class PostRead(PostCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_creation: datetime
    id_user: int
