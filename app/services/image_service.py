from __future__ import annotations

from io import BytesIO

from PIL import Image, UnidentifiedImageError

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


def validate_image(content: bytes, mime_type: str, max_bytes: int) -> None:
    if mime_type not in ALLOWED_TYPES:
        raise ValueError("Only JPG, PNG and WEBP images are supported.")
    if len(content) > max_bytes:
        raise ValueError("The uploaded image is too large.")
    try:
        with Image.open(BytesIO(content)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError):
        raise ValueError("The uploaded file is not a valid image.")
