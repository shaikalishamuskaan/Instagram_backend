import hashlib
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dbms.models import Image


def read_image(path: str) -> tuple[bytes, str]:
    image_path = Path(path)

    image_data = image_path.read_bytes()

    image_hash = hashlib.sha256(image_data).hexdigest()

    return image_data, image_hash


async def get_or_create_image(
    session: AsyncSession,
    image_data: bytes,
    image_hash: str,
) -> Image:
    result = await session.execute(select(Image).where(Image.image_hash == image_hash))

    image = result.scalar_one_or_none()

    if image:
        return image

    image = Image(
        image_data=image_data,
        image_hash=image_hash,
    )

    session.add(image)

    await session.commit()
    await session.refresh(image)

    return image
