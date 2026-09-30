import pytest
from pydantic import ValidationError

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


def test_user_create_valid():
    user = UserCreate(
        name="Alice",
        email="ALICE@EXAMPLE.COM",
    )

    assert user.name == "Alice"
    assert user.email == "alice@example.com"


def test_user_email_is_normalized():
    user = UserCreate(
        name="Alice",
        email="  Alice@Example.COM  ",
    )

    assert user.email == "alice@example.com"


def test_user_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(
            name="Alice",
            email="not-an-email",
        )


def test_user_empty_name():
    with pytest.raises(ValidationError):
        UserCreate(
            name="",
            email="alice@example.com",
        )


def test_user_update_valid():
    user = UserUpdate(
        name="Bob",
        email="bob@example.com",
    )

    assert user.name == "Bob"
    assert user.email == "bob@example.com"


def test_post_create_valid():
    post = PostCreate(
        user_id=1,
        image_path="photo.jpg",
        caption="My vacation",
    )

    assert post.user_id == 1
    assert post.image_path == "photo.jpg"
    assert post.caption == "My vacation"


def test_post_create_invalid_user_id():
    with pytest.raises(ValidationError):
        PostCreate(
            user_id=0,
            image_path="photo.jpg",
            caption="Hello",
        )


def test_post_blank_caption_becomes_none():
    post = PostCreate(
        user_id=1,
        image_path="photo.jpg",
        caption="   ",
    )

    assert post.caption is None


def test_post_update_valid():
    post = PostUpdate(
        post_id=1,
        caption="Updated caption",
    )

    assert post.post_id == 1
    assert post.caption == "Updated caption"


def test_comment_create_valid():
    comment = CommentCreate(
        user_id=1,
        post_id=2,
        comment_text="Nice post!",
    )

    assert comment.user_id == 1
    assert comment.post_id == 2
    assert comment.comment_text == "Nice post!"


def test_comment_create_invalid_user_id():
    with pytest.raises(ValidationError):
        CommentCreate(
            user_id=0,
            post_id=1,
            comment_text="Nice post!",
        )


def test_comment_update_valid():
    comment = CommentUpdate(
        comment_id=1,
        comment_text="Updated comment",
    )

    assert comment.comment_id == 1
    assert comment.comment_text == "Updated comment"


def test_reaction_like():
    reaction = ReactionCreate(
        user_id=1,
        post_id=2,
        reaction_type="LIKE",
    )

    assert reaction.reaction_type == "LIKE"


def test_reaction_dislike():
    reaction = ReactionCreate(
        user_id=1,
        post_id=2,
        reaction_type="DISLIKE",
    )

    assert reaction.reaction_type == "DISLIKE"


def test_reaction_invalid_type():
    with pytest.raises(ValidationError):
        ReactionCreate(
            user_id=1,
            post_id=2,
            reaction_type="LOVE",
        )


def test_id_must_be_positive():
    with pytest.raises(ValidationError):
        IdInput(id=0)

    with pytest.raises(ValidationError):
        IdInput(id=-5)


def test_page_must_be_positive():
    with pytest.raises(ValidationError):
        PageInput(page=0)

    with pytest.raises(ValidationError):
        PageInput(page=-1)


def test_extra_fields_are_rejected():
    with pytest.raises(ValidationError):
        UserCreate(
            name="Alice",
            email="alice@example.com",
            age=25,
        )


def test_whitespace_is_stripped():
    user = UserCreate(
        name="  Alice  ",
        email="alice@example.com",
    )

    assert user.name == "Alice"