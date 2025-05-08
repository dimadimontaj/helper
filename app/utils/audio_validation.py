import mimetypes
from typing import Set

from fastapi import HTTPException, UploadFile, status


SUPPORTED_MIME: Set[str] = {
    "audio/ogg",
    "audio/mpeg",
    "audio/flac",
    "audio/wav",
}


def detect_mime(filename: str, fallback: str | None = None) -> str:
    mime, _ = mimetypes.guess_type(filename, strict=True)
    return mime or (fallback or "")


def validate_audio_file(file: UploadFile) -> str:
    if not file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Только аудиофайлы поддерживаются.",
        )

    mime = detect_mime(file.filename, file.content_type)

    if mime not in SUPPORTED_MIME:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Неподдерживаемый аудиоформат.",
        )
    return mime
