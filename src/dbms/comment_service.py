from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from dbms.models import Comment


async def add_comment(
    session: AsyncSession,
    user_id: int,
    post_id: int,
    comment_text: str,
) -> Comment:
    if not comment_text:
        raise ValueError("Comment cannot be empty.")

    comment = Comment(
        user_id=user_id,
        post_id=post_id,
        comment_text=comment_text,
    )

    session.add(comment)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ValueError("Duplicate comment: you already added this exact comment.")

    await session.refresh(comment)

    return comment
async def update_comment(
    session: AsyncSession,
    comment_id: int,
    comment_text: str,
) -> Comment:
    result = await session.execute(
        select(Comment).where(Comment.id == comment_id)
    )

    comment = result.scalar_one_or_none()

    if comment is None:
        raise ValueError("Comment does not exist.")

    comment.comment_text = comment_text

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ValueError(
            "You already have the same comment on this post."
        )

    await session.refresh(comment)

    return comment


async def delete_comment(
    session: AsyncSession,
    comment_id: int,
) -> None:
    result = await session.execute(
        select(Comment).where(Comment.id == comment_id)
    )

    comment = result.scalar_one_or_none()

    if comment is None:
        raise ValueError("Comment does not exist.")

    await session.delete(comment)

    await session.commit()