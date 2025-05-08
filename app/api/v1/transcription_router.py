from fastapi import APIRouter, UploadFile, File, Request, status, Depends, HTTPException

from app.core.dependencies import get_transcription_service
from app.services.transcription_service import TranscriptionServiceProtocol, TranscriptionServiceError

from app.schemas.schemas import TranscriptionResponse
from app.utils.logging import logger
from app.utils.audio_validation import validate_audio_file

router = APIRouter()


@router.post("/", response_model=TranscriptionResponse, status_code=status.HTTP_200_OK)
async def transcribe(
    request: Request,
    file: UploadFile = File(...),
    transcription: TranscriptionServiceProtocol = Depends(get_transcription_service),
):
    client_ip = request.headers.get("X-Forwarded-For", request.client.host)
    logger.info("Received /transcribe from %s, filename=%s", client_ip, file.filename)

    mime = validate_audio_file(file)

    try:
        transcript = await transcription.transcribe(
            file_name=file.filename,
            file_bytes=await file.read(),
            mime=mime,
        )
    except TranscriptionServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return TranscriptionResponse(transcript=transcript)
