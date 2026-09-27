from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dbms.models import Post, Reaction, User


async def change_reaction(
    session: AsyncSession,
    user_id: int,
    post_id: int,
    reaction_type: str,
) -> str:
    if reaction_type not in {"LIKE", "DISLIKE"}:
        raise ValueError("Reaction must be LIKE or DISLIKE.")
    
    result = await session.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise ValueError("User does not exist.")


    result = await session.execute(
        select(Post).where(Post.id == post_id).with_for_update()
    )

    post = result.scalar_one_or_none()

    if post is None:
        raise ValueError("Post does not exist.")

    result = await session.execute(
        select(Reaction).where(
            Reaction.user_id == user_id,
            Reaction.post_id == post_id,
        )
    )

    reaction = result.scalar_one_or_none()

    if reaction is None:
        reaction = Reaction(
            user_id=user_id,
            post_id=post_id,
            reaction_type=reaction_type,
        )

        session.add(reaction)

        if reaction_type == "LIKE":
            post.like_count += 1
        else:
            post.dislike_count += 1

        await session.commit()

        return reaction_type

    if reaction.reaction_type == reaction_type:
        if reaction_type == "LIKE":
            post.like_count -= 1
        else:
            post.dislike_count -= 1

        await session.delete(reaction)
        await session.commit()

        return "NEUTRAL"



   
    old_reaction = reaction.reaction_type

    reaction.reaction_type = reaction_type

    if old_reaction == "LIKE":
        post.like_count -= 1
        post.dislike_count += 1
    else:
        post.dislike_count -= 1
        post.like_count += 1

    await session.commit()

    return reaction_type
