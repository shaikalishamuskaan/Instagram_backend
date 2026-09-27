from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from dbms.image_service import read_image
from dbms.models import Comment, Image, Post, Reaction


async def create_post(
    session: AsyncSession,
    user_id: int,
    image_path: str,
    caption: str | None,
) -> Post:
    image_data, image_hash = read_image(image_path)

    result = await session.execute(select(Image).where(Image.image_hash == image_hash))

    image = result.scalar_one_or_none()

    if image is None:
        image = Image(
            image_data=image_data,
            image_hash=image_hash,
        )

        session.add(image)
        await session.flush()

    post = Post(
        user_id=user_id,
        image_id=image.id,
        caption=caption,
    )

    session.add(post)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ValueError("Duplicate post: this image and caption already exist.")

    await session.refresh(post)

    return post

async def delete_post(session: AsyncSession, post_id: int) -> None:
    result = await session.execute(
        select(Post).where(Post.id == post_id)
    )

    post = result.scalar_one_or_none()

    if post is None:
        raise ValueError("Post does not exist.")

    await session.execute(
        delete(Reaction).where(Reaction.post_id == post_id)
    )

    await session.execute(
        delete(Comment).where(Comment.post_id == post_id)
    )

    await session.delete(post)

    await session.commit()
    
async def update_post(
    session: AsyncSession,
    post_id: int,
    caption: str | None,
) -> Post:
    result = await session.execute(
        select(Post).where(Post.id == post_id)
    )

    post = result.scalar_one_or_none()

    if post is None:
        raise ValueError("Post does not exist.")

    post.caption = caption

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ValueError(
            "A post with this image and caption already exists."
        )

    await session.refresh(post)

    return post