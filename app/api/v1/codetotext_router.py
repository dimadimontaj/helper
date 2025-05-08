from fastapi import APIRouter, UploadFile, File, Request, HTTPException, status, Depends

from app.core.dependencies import get_ocr_service, get_llm_service, get_prompt_service
from app.services.ocr_service import OCRServiceProtocol, OCRServiceError
from app.services.llm_service import LLMServiceProtocol, LLMServiceError
from app.services.prompt_service import PromptServiceProtocol

from app.schemas.schemas import CodetotextResponse
from app.utils.logging import logger


router = APIRouter()

PROMPT_PATH = "codeformatter/v1_system.j2"


@router.post("/", response_model=CodetotextResponse, status_code=status.HTTP_200_OK)
async def codetotext(
    request: Request,
    file: UploadFile = File(...),
    ocr: OCRServiceProtocol = Depends(get_ocr_service),
    llm: LLMServiceProtocol = Depends(get_llm_service),
    prompts: PromptServiceProtocol = Depends(get_prompt_service),
):
    client_ip = request.headers.get("X-Forwarded-For", request.client.host)
    logger.info("Received /codetotext from %s, filename=%s", client_ip, file.filename)

    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Только фото.")

    try:
        row_code = await ocr.parse_image(
            file_name=file.filename,
            file_bytes=await file.read(),
        )
    except OCRServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    messages = (((prompts.new_builder()
                .add_system(path=PROMPT_PATH))
                .add_user(content=row_code))
                .build())

    try:
        code = await llm.query_llm(
            model="code_formatter",
            messages=messages,
        )
    except LLMServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return CodetotextResponse(code=code)
