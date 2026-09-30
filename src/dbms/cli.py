import asyncio

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from dbms.comment_service import add_comment as create_comment
from dbms.comment_service import delete_comment, update_comment
from dbms.db import SessionLocal
from dbms.models import Comment, Post, Reaction, User
from dbms.post_service import create_post, delete_post, update_post
from dbms.reaction_service import change_reaction
from dbms.schemas import (
    CommentCreate,
    CommentUpdate,
    IdInput,
    PageInput,
    PostCreate,
    PostUpdate,
    ReactionCreate,
    UserCreate,
    UserUpdate,
)


async def show_db_state():
    async with SessionLocal() as session:
        users_result = await session.execute(
            select(User).order_by(User.id)
        )
        users = users_result.scalars().all()

        posts_result = await session.execute(
            select(Post).order_by(Post.id)
        )
        posts = posts_result.scalars().all()

        reactions_result = await session.execute(
            select(Reaction).order_by(Reaction.id)
        )
        reactions = reactions_result.scalars().all()

        comments_result = await session.execute(
            select(Comment).order_by(Comment.id)
        )
        comments = comments_result.scalars().all()

        print("\n========== USERS ==========\n")

        for user in users:
            print(f"User ID: {user.id}")
            print(f"Name: {user.name}")
            print(f"Email: {user.email}")
            print("-" * 35)

        print("\n========== POSTS ==========\n")

        for post in posts:
            print(f"Post ID: {post.id}")
            print(f"User ID: {post.user_id}")
            print(f"Image ID: {post.image_id}")
            print(f"Caption: {post.caption}")
            print(f"Likes: {post.like_count}")
            print(f"Dislikes: {post.dislike_count}")
            print("-" * 35)

        print("\n========== REACTIONS ==========\n")

        for reaction in reactions:
            print(f"Reaction ID: {reaction.id}")
            print(f"User ID: {reaction.user_id}")
            print(f"Post ID: {reaction.post_id}")
            print(f"Type: {reaction.reaction_type}")
            print("-" * 35)

        print("\n========== COMMENTS ==========\n")

        for comment in comments:
            print(f"Comment ID: {comment.id}")
            print(f"User ID: {comment.user_id}")
            print(f"Post ID: {comment.post_id}")
            print(f"Comment: {comment.comment_text}")
            print("-" * 35)


# ============================================================
# USERS
# ============================================================


async def create_user(username: str, email: str):
    try:
        user_data = UserCreate(
            name=username,
            email=email,
        )
    except ValueError as error:
        print("Invalid user data.")
        print(error)
        return

    async with SessionLocal() as session:
        user = User(
            name=user_data.name,
            email=str(user_data.email),
        )

        session.add(user)

        try:
            await session.commit()
            await session.refresh(user)

            print("User created successfully.")
            print(f"User ID: {user.id}")
            print(f"Name: {user.name}")
            print(f"Email: {user.email}")

        except IntegrityError:
            await session.rollback()
            print("User with this name and email already exists.")


async def view_users():
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).order_by(User.id)
        )

        users = result.scalars().all()

        if not users:
            print("No users found.")
            return

        print("\n========== USERS ==========\n")

        for user in users:
            print(f"User ID: {user.id}")
            print(f"Name: {user.name}")
            print(f"Email: {user.email}")
            print(f"Created: {user.created_at}")
            print("-" * 35)


async def update_user(user_id: int):
    try:
        id_data = IdInput(id=user_id)
    except ValueError:
        print("User ID must be a positive number.")
        return

    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.id == id_data.id)
        )

        user = result.scalar_one_or_none()

        if user is None:
            print("User does not exist.")
            return

        new_name = input("Enter new name: ")
        new_email = input("Enter new email: ")

        try:
            user_data = UserUpdate(
                name=new_name,
                email=new_email,
            )
        except ValueError as error:
            print("Invalid user data.")
            print(error)
            return

        if (
            user_data.name.lower() == user.name.lower()
            and str(user_data.email).lower() == user.email.lower()
        ):
            print("No changes made.")
            return

        user.name = user_data.name
        user.email = str(user_data.email)

        try:
            await session.commit()
            print("User updated successfully.")

        except IntegrityError:
            await session.rollback()
            print(
                "Another user already exists with this name and email."
            )


async def delete_user(user_id: int):
    try:
        id_data = IdInput(id=user_id)
    except ValueError:
        print("User ID must be a positive number.")
        return

    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.id == id_data.id)
        )

        user = result.scalar_one_or_none()

        if user is None:
            print("User does not exist.")
            return

        result = await session.execute(
            select(Post.id).where(Post.user_id == id_data.id)
        )

        if result.first():
            print("Cannot delete user because the user has posts.")
            return

        result = await session.execute(
            select(Comment.id).where(Comment.user_id == id_data.id)
        )

        if result.first():
            print("Cannot delete user because the user has comments.")
            return

        result = await session.execute(
            select(Reaction.id).where(Reaction.user_id == id_data.id)
        )

        if result.first():
            print("Cannot delete user because the user has reactions.")
            return

        await session.delete(user)
        await session.commit()

        print("User deleted successfully.")


# ============================================================
# POSTS
# ============================================================


async def create_post_command(
    user_id: int,
    image_path: str,
    caption: str | None,
):
    try:
        post_data = PostCreate(
            user_id=user_id,
            image_path=image_path,
            caption=caption,
        )
    except ValueError as error:
        print("Invalid post data.")
        print(error)
        return

    async with SessionLocal() as session:
        try:
            post = await create_post(
                session=session,
                user_id=post_data.user_id,
                image_path=post_data.image_path,
                caption=post_data.caption,
            )

            print("Post created successfully.")
            print(f"Post ID: {post.id}")
            print(f"User ID: {post.user_id}")
            print(f"Image ID: {post.image_id}")
            print(f"Caption: {post.caption}")

        except ValueError as error:
            print(error)


async def update_post_command(
    post_id: int,
    caption: str | None,
):
    try:
        post_data = PostUpdate(
            post_id=post_id,
            caption=caption,
        )
    except ValueError as error:
        print("Invalid post data.")
        print(error)
        return

    async with SessionLocal() as session:
        try:
            post = await update_post(
                session=session,
                post_id=post_data.post_id,
                caption=post_data.caption,
            )

            print("Post updated successfully.")
            print(f"Post ID: {post.id}")
            print(f"Caption: {post.caption}")

        except ValueError as error:
            print(error)


async def list_posts(page: int):
    try:
        page_data = PageInput(page=page)
    except ValueError as error:
        print("Invalid page number.")
        print(error)
        return

    posts_per_page = 10
    offset = (page_data.page - 1) * posts_per_page

    async with SessionLocal() as session:
        result = await session.execute(
            select(Post)
            .order_by(Post.id)
            .limit(posts_per_page)
            .offset(offset)
        )

        posts = result.scalars().all()

        if not posts:
            print("No posts found on this page.")
            return

        print(f"\n========== PAGE {page_data.page} ==========\n")

        for post in posts:
            print(f"Post ID: {post.id}")
            print(f"User ID: {post.user_id}")
            print(f"Caption: {post.caption}")
            print(f"Likes: {post.like_count}")
            print(f"Dislikes: {post.dislike_count}")
            print("-" * 35)


async def show_post(post_id: int):
    try:
        id_data = IdInput(id=post_id)
    except ValueError:
        print("Post ID must be a positive number.")
        return

    async with SessionLocal() as session:
        result = await session.execute(
            select(Post).where(Post.id == id_data.id)
        )

        post = result.scalar_one_or_none()

        if post is None:
            print(f"Post {id_data.id} was not found.")
            return

        print("\n========== POST ==========\n")
        print(f"Post ID: {post.id}")
        print(f"User ID: {post.user_id}")
        print(f"Image ID: {post.image_id}")
        print(f"Caption: {post.caption}")
        print(f"Likes: {post.like_count}")
        print(f"Dislikes: {post.dislike_count}")
        print(f"Created: {post.created_at}")


async def delete_post_command(post_id: int):
    try:
        id_data = IdInput(id=post_id)
    except ValueError:
        print("Post ID must be a positive number.")
        return

    async with SessionLocal() as session:
        try:
            await delete_post(
                session=session,
                post_id=id_data.id,
            )

            print("Post deleted successfully.")

        except ValueError as error:
            print(error)


# ============================================================
# COMMENTS
# ============================================================


async def add_comment(
    post_id: int,
    user_id: int,
    comment_text: str,
):
    try:
        comment_data = CommentCreate(
            post_id=post_id,
            user_id=user_id,
            comment_text=comment_text,
        )
    except ValueError as error:
        print("Invalid comment data.")
        print(error)
        return

    async with SessionLocal() as session:
        try:
            comment = await create_comment(
                session=session,
                user_id=comment_data.user_id,
                post_id=comment_data.post_id,
                comment_text=comment_data.comment_text,
            )

            print("Comment added successfully.")
            print(f"Comment ID: {comment.id}")
            print(f"User ID: {comment.user_id}")
            print(f"Post ID: {comment.post_id}")
            print(f"Comment: {comment.comment_text}")

        except ValueError as error:
            print(error)


async def update_comment_command(
    comment_id: int,
    comment_text: str,
):
    try:
        comment_data = CommentUpdate(
            comment_id=comment_id,
            comment_text=comment_text,
        )
    except ValueError as error:
        print("Invalid comment data.")
        print(error)
        return

    async with SessionLocal() as session:
        try:
            comment = await update_comment(
                session=session,
                comment_id=comment_data.comment_id,
                comment_text=comment_data.comment_text,
            )

            print("Comment updated successfully.")
            print(f"Comment ID: {comment.id}")
            print(f"Comment: {comment.comment_text}")

        except ValueError as error:
            print(error)


async def delete_comment_command(comment_id: int):
    try:
        id_data = IdInput(id=comment_id)
    except ValueError:
        print("Comment ID must be a positive number.")
        return

    async with SessionLocal() as session:
        try:
            await delete_comment(
                session=session,
                comment_id=id_data.id,
            )

            print("Comment deleted successfully.")

        except ValueError as error:
            print(error)


async def show_comments(post_id: int):
    try:
        id_data = IdInput(id=post_id)
    except ValueError:
        print("Post ID must be a positive number.")
        return

    async with SessionLocal() as session:
        result = await session.execute(
            select(Comment)
            .where(Comment.post_id == id_data.id)
            .order_by(Comment.id)
        )

        comments = result.scalars().all()

        if not comments:
            print("No comments found.")
            return

        print(
            f"\n========== COMMENTS FOR POST {id_data.id} ==========\n"
        )

        for comment in comments:
            print(f"Comment ID: {comment.id}")
            print(f"User ID: {comment.user_id}")
            print(f"Comment: {comment.comment_text}")
            print(f"Created: {comment.created_at}")
            print("-" * 35)


# ============================================================
# REACTIONS
# ============================================================


async def like_post(post_id: int, user_id: int):
    try:
        reaction_data = ReactionCreate(
            user_id=user_id,
            post_id=post_id,
            reaction_type="LIKE",
        )
    except ValueError as error:
        print("Invalid reaction data.")
        print(error)
        return

    async with SessionLocal() as session:
        try:
            result = await change_reaction(
                session=session,
                user_id=reaction_data.user_id,
                post_id=reaction_data.post_id,
                reaction_type=reaction_data.reaction_type,
            )

            print(f"User {user_id}: {result}")

        except ValueError as error:
            print(error)


async def dislike_post(post_id: int, user_id: int):
    try:
        reaction_data = ReactionCreate(
            user_id=user_id,
            post_id=post_id,
            reaction_type="DISLIKE",
        )
    except ValueError as error:
        print("Invalid reaction data.")
        print(error)
        return

    async with SessionLocal() as session:
        try:
            result = await change_reaction(
                session=session,
                user_id=reaction_data.user_id,
                post_id=reaction_data.post_id,
                reaction_type=reaction_data.reaction_type,
            )

            print(f"User {user_id}: {result}")

        except ValueError as error:
            print(error)


async def view_reactions(post_id: int):
    try:
        id_data = IdInput(id=post_id)
    except ValueError:
        print("Post ID must be a positive number.")
        return

    async with SessionLocal() as session:
        result = await session.execute(
            select(Reaction)
            .where(Reaction.post_id == id_data.id)
            .order_by(Reaction.id)
        )

        reactions = result.scalars().all()

        if not reactions:
            print("No reactions found.")
            return

        print(
            f"\n========== REACTIONS FOR POST {id_data.id} ==========\n"
        )

        for reaction in reactions:
            print(f"Reaction ID: {reaction.id}")
            print(f"User ID: {reaction.user_id}")
            print(f"Post ID: {reaction.post_id}")
            print(f"Type: {reaction.reaction_type}")
            print(f"Created: {reaction.created_at}")
            print("-" * 35)


async def remove_reaction(post_id: int, user_id: int):
    try:
        post_data = IdInput(id=post_id)
        user_data = IdInput(id=user_id)
    except ValueError:
        print("Post ID and user ID must be positive numbers.")
        return

    async with SessionLocal() as session:
        result = await session.execute(
            select(Reaction).where(
                Reaction.post_id == post_data.id,
                Reaction.user_id == user_data.id,
            )
        )

        reaction = result.scalar_one_or_none()

        if reaction is None:
            print("Reaction does not exist.")
            return

        result = await session.execute(
            select(Post).where(Post.id == post_data.id)
        )

        post = result.scalar_one_or_none()

        if post is None:
            print("Post does not exist.")
            return

        if reaction.reaction_type == "LIKE":
            post.like_count -= 1
        else:
            post.dislike_count -= 1

        await session.delete(reaction)
        await session.commit()

        print("Reaction removed successfully.")


# ============================================================
# INPUT
# ============================================================


def get_integer_input(message: str) -> int:
    while True:
        try:
            return int(input(message))
        except ValueError:
            print("Please enter a valid number.")


# ============================================================
# MAIN MENU
# ============================================================


async def main():
    while True:
        print("\n========== INSTAGRAM DB ==========")

        print("\n----- USERS -----")
        print("1.  Create User")
        print("2.  View Users")
        print("3.  Update User")
        print("4.  Delete User")

        print("\n----- POSTS -----")
        print("5.  Create Post")
        print("6.  View Posts")
        print("7.  Update Post")
        print("8.  Delete Post")

        print("\n----- COMMENTS -----")
        print("9.  Create Comment")
        print("10. View Comments")
        print("11. Update Comment")
        print("12. Delete Comment")

        print("\n----- POST REACTIONS -----")
        print("13. Like Post")
        print("14. Dislike Post")
        print("15. View Reactions")
        print("16. Remove Reaction")

        print("\n----- DATABASE -----")
        print("17. Show Database State")
        print("0. Exit")

        choice = input("\nEnter your choice: ").strip()

        # ---------------- USERS ----------------

        if choice == "1":
            username = input("Enter user name: ")
            email = input("Enter email: ")

            await create_user(username, email)

        elif choice == "2":
            await view_users()

        elif choice == "3":
            user_id = get_integer_input("Enter user ID: ")
            await update_user(user_id)

        elif choice == "4":
            user_id = get_integer_input("Enter user ID: ")
            await delete_user(user_id)

        # ---------------- POSTS ----------------

        elif choice == "5":
            user_id = get_integer_input("Enter user ID: ")

            image_path = (
                input("Enter image path: ")
                .strip()
                .strip('"')
            )

            caption = input("Enter caption: ")

            await create_post_command(
                user_id,
                image_path,
                caption,
            )

        elif choice == "6":
            page = get_integer_input("Enter page number: ")
            await list_posts(page)

        elif choice == "7":
            post_id = get_integer_input("Enter post ID: ")
            caption = input("Enter new caption: ")

            await update_post_command(
                post_id,
                caption,
            )

        elif choice == "8":
            post_id = get_integer_input("Enter post ID: ")
            await delete_post_command(post_id)

        # ---------------- COMMENTS ----------------

        elif choice == "9":
            post_id = get_integer_input("Enter post ID: ")
            user_id = get_integer_input("Enter user ID: ")
            comment_text = input("Enter comment: ")

            await add_comment(
                post_id,
                user_id,
                comment_text,
            )

        elif choice == "10":
            post_id = get_integer_input("Enter post ID: ")
            await show_comments(post_id)

        elif choice == "11":
            comment_id = get_integer_input("Enter comment ID: ")
            comment_text = input("Enter new comment: ")

            await update_comment_command(
                comment_id,
                comment_text,
            )

        elif choice == "12":
            comment_id = get_integer_input("Enter comment ID: ")
            await delete_comment_command(comment_id)

        # ---------------- REACTIONS ----------------

        elif choice == "13":
            post_id = get_integer_input("Enter post ID: ")
            user_id = get_integer_input("Enter user ID: ")

            await like_post(
                post_id,
                user_id,
            )

        elif choice == "14":
            post_id = get_integer_input("Enter post ID: ")
            user_id = get_integer_input("Enter user ID: ")

            await dislike_post(
                post_id,
                user_id,
            )

        elif choice == "15":
            post_id = get_integer_input("Enter post ID: ")
            await view_reactions(post_id)

        elif choice == "16":
            post_id = get_integer_input("Enter post ID: ")
            user_id = get_integer_input("Enter user ID: ")

            await remove_reaction(
                post_id,
                user_id,
            )

        # ---------------- DATABASE ----------------

        elif choice == "17":
            await show_db_state()

        elif choice == "0":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    asyncio.run(main())