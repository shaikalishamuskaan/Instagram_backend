from datetime import UTC, datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    LargeBinary,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    __table_args__ = (
        UniqueConstraint(
            "name",
            "email",
            name="uq_users_name_email",
        ),
    )


class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True)

    image_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )

    image_data: Mapped[bytes] = mapped_column(
        LargeBinary,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )


class Post(Base):
    __tablename__ = "posts"
    __table_args__ = (
        Index(
            "uq_post_image_caption",
            "image_id",
            "caption",
            unique=True,
            postgresql_nulls_not_distinct=True,
        ),
        Index("ix_posts_user_id", "user_id"),
        Index("ix_posts_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    image_id: Mapped[int] = mapped_column(
        ForeignKey("images.id"),
        nullable=False,
    )

    caption: Mapped[str | None] = mapped_column(
        nullable=True,
    )

    like_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    dislike_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )


class Reaction(Base):
    __tablename__ = "reactions"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id"),
        nullable=False,
    )

    reaction_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    __table_args__ = (
        CheckConstraint(
            "reaction_type IN ('LIKE', 'DISLIKE')",
            name="check_reaction_type",
        ),
        Index(
            "uq_reactions_user_post",
            "user_id",
            "post_id",
            unique=True,
        ),
        Index("ix_reactions_post_id", "post_id"),
    )


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id"),
        nullable=False,
    )

    comment_text: Mapped[str] = mapped_column(
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    __table_args__ = (
        Index(
            "uq_comments_user_post_text",
            "user_id",
            "post_id",
            "comment_text",
            unique=True,
        ),
        Index("ix_comments_post_id", "post_id"),
    )
