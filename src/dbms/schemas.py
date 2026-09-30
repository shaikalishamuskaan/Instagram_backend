# from pydantic import BaseModel, EmailStr, Field


# class UserCreate(BaseModel):
#     name: str = Field(min_length=1, max_length=100)
#     email: EmailStr


# class UserUpdate(BaseModel):
#     name: str = Field(min_length=1, max_length=100)
#     email: EmailStr


from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    PositiveInt,
    field_validator,
)


class SchemaBase(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        validate_assignment=True,
    )


class UserCreate(SchemaBase):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., max_length=254)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return str(value).strip().lower()


class UserUpdate(UserCreate):
    pass


class PostCreate(SchemaBase):
    user_id: PositiveInt
    image_path: str = Field(..., min_length=1, max_length=500)
    caption: str | None = Field(default=None, max_length=2_200)

    @field_validator("caption", mode="before")
    @classmethod
    def validate_caption(cls, value: str | None) -> str | None:
        if value is None or not str(value).strip():
            return None
        return str(value).strip()


class PostUpdate(SchemaBase):
    post_id: PositiveInt
    caption: str | None = Field(default=None, max_length=2_200)

    @field_validator("caption", mode="before")
    @classmethod
    def validate_caption(cls, value: str | None) -> str | None:
        if value is None or not str(value).strip():
            return None
        return str(value).strip()


class CommentCreate(SchemaBase):
    user_id: PositiveInt
    post_id: PositiveInt
    comment_text: str = Field(..., min_length=1, max_length=2_200)


class CommentUpdate(SchemaBase):
    comment_id: PositiveInt
    comment_text: str = Field(..., min_length=1, max_length=2_200)


class ReactionCreate(SchemaBase):
    user_id: PositiveInt
    post_id: PositiveInt
    reaction_type: Literal["LIKE", "DISLIKE"]


class IdInput(SchemaBase):
    id: PositiveInt


class PageInput(SchemaBase):
    page: PositiveInt