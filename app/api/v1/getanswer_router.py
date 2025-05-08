from fastapi import APIRouter, Request, status, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.core.dependencies import get_llm_service, get_prompt_service
from app.services.llm_service import LLMServiceProtocol, LLMServiceError
from app.services.prompt_service import PromptServiceProtocol

from app.schemas.schemas import QueryGetAnswerTheoryPayload, GetAnswerTheoryResponse
from app.utils.logging import logger


router = APIRouter()

FAST_SYSTEM_PROMPT_PATH = "theory/fast/v1_system.j2"
FAST_ASSISTANT_PROMPT_PATH = "theory/fast/v1_assistant.j2"
LONG_SYSTEM_PROMPT_PATH = "theory/long/v1_system.j2"
LONG_ASSISTANT_PROMPT_PATH = "theory/long/v1_assistant.j2"


@router.post("/theory/fast/", status_code=status.HTTP_200_OK)
async def get_fast_answer_theory(
    request: Request,
    payload: QueryGetAnswerTheoryPayload,
    llm: LLMServiceProtocol = Depends(get_llm_service),
    prompts: PromptServiceProtocol = Depends(get_prompt_service),
):
    client_ip = request.headers.get("X-Forwarded-For", request.client.host)
    logger.info("Received /theory/fast/ from %s, filename=%s, context=%s, llm=%s",
                client_ip,
                payload.question,
                payload.context,
                payload.model,
                )

    messages = (((prompts.new_builder()
                    .add_system(path=FAST_SYSTEM_PROMPT_PATH, position=payload.context.position, grade=payload.context.grade))
                    .add_user(content=payload.question))
                    .add_assistant(path=FAST_ASSISTANT_PROMPT_PATH)
                    .build())

    try:
        async def sse():
            async for chunk in llm.stream_query_llm(model=payload.model, messages=messages):
                yield chunk
    except LLMServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return StreamingResponse(
        sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/theory/long/", response_model=GetAnswerTheoryResponse, status_code=status.HTTP_200_OK)
async def get_long_answer_theory(
    request: Request,
    payload: QueryGetAnswerTheoryPayload,
    llm: LLMServiceProtocol = Depends(get_llm_service),
    prompts: PromptServiceProtocol = Depends(get_prompt_service),
):
    client_ip = request.headers.get("X-Forwarded-For", request.client.host)
    logger.info("Received /theory/long/ from %s, filename=%s, context=%s, llm=%s",
                client_ip,
                payload.question,
                payload.context,
                payload.model,
                )

    messages = (((prompts.new_builder()
                    .add_system(path=LONG_SYSTEM_PROMPT_PATH, position=payload.context.position, grade=payload.context.grade))
                    .add_user(content=payload.question))
                    .add_assistant(path=LONG_ASSISTANT_PROMPT_PATH)
                    .build())

    try:
        long_answer = await llm.query_llm(model=payload.model, messages=messages)
    except LLMServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return GetAnswerTheoryResponse(answer=long_answer, type="long")






























































# from fastapi import APIRouter, Request, status, Depends, HTTPException
# from fastapi.responses import StreamingResponse
# from pydantic import BaseModel
#
# from app.core.dependencies import get_llm_service, get_prompt_service, get_app_settings
# from app.services.llm_service import LLMServiceProtocol, LLMServiceError
# from app.services.prompt_service import PromptServiceProtocol
#
# from app.core.settings.base import AppSettings
# from app.schemas.schemas import GetAnswerTheoryResponse
# from app.utils.logging import logger
#
#
# router = APIRouter()
#
# FAST_SYSTEM_PROMPT_PATH = "theory/fast/v1_system.j2"
# FAST_ASSISTANT_PROMPT_PATH = "theory/fast/v1_assistant.j2"
# LONG_SYSTEM_PROMPT_PATH = "theory/long/v1_system.j2"
# LONG_ASSISTANT_PROMPT_PATH = "theory/long/v1_assistant.j2"
#
#
# class ContextData(BaseModel):
#     position: str
#     grade: str
#
#
# class QueryPayload(BaseModel):
#     question: str
#     context: ContextData
#     llm: str
#
#
# @router.post("/theory/", response_model=GetAnswerTheoryResponse, status_code=status.HTTP_200_OK)
# async def get_answer_theory(
#     request: Request,
#     payload: QueryPayload,
#     llm: LLMServiceProtocol = Depends(get_llm_service),
#     prompts: PromptServiceProtocol = Depends(get_prompt_service),
#     cfg: AppSettings = Depends(get_app_settings),
# ):
#     client_ip = request.headers.get("X-Forwarded-For", request.client.host)
#     logger.info("Received /theory from %s, filename=%s, context=%s, llm=%s",
#                 client_ip,
#                 payload.question,
#                 payload.context,
#                 payload.llm,
#                 )
#
#     async def answer_stream():
#
#         fast_messages = (((prompts.new_builder()
#                         .add_system(path=FAST_SYSTEM_PROMPT_PATH, position=payload.context.position, grade=payload.context.grade))
#                         .add_user(content=payload.question))
#                         .add_assistant(path=FAST_ASSISTANT_PROMPT_PATH)
#                         .build())
#
#         try:
#             fast_answer = await llm.query_llm(
#                 model=cfg.llm_gpt_4_1_nano.model,
#                 messages=fast_messages,
#                 temperature=cfg.llm_gpt_4_1_nano.temperature,
#                 top_p=cfg.llm_gpt_4_1_nano.top_p,
#                 max_tokens=cfg.llm_gpt_4_1_nano.max_tokens,
#                 frequency_penalty=cfg.llm_gpt_4_1_nano.frequency_penalty,
#                 presence_penalty=cfg.llm_gpt_4_1_nano.presence_penalty
#             )
#         except LLMServiceError as exc:
#             raise HTTPException(status_code=502, detail=str(exc)) from exc
#
#         yield GetAnswerTheoryResponse(answer=fast_answer, type="fast").json().encode("utf-8") + b"\n\n"
#
#         long_messages = (((prompts.new_builder()
#                         .add_system(path=LONG_SYSTEM_PROMPT_PATH, position=payload.context.position, grade=payload.context.grade))
#                         .add_user(content=payload.question))
#                         .add_assistant(path=LONG_ASSISTANT_PROMPT_PATH)
#                         .build())
#
#         try:
#             long_answer = await llm.query_llm(
#                 model=cfg.llm_o4_mini_high.model,
#                 messages=long_messages,
#                 temperature=cfg.llm_o4_mini_high.temperature,
#                 top_p=cfg.llm_o4_mini_high.top_p,
#                 max_tokens=cfg.llm_o4_mini_high.max_tokens,
#                 frequency_penalty=cfg.llm_o4_mini_high.frequency_penalty,
#                 presence_penalty=cfg.llm_o4_mini_high.presence_penalty,
#                 reasoning_effort=cfg.llm_o4_mini_high.reasoning_effort,
#                 stop=cfg.llm_o4_mini_high.stop,
#             )
#         except LLMServiceError as exc:
#             raise HTTPException(status_code=502, detail=str(exc)) from exc
#
#         yield GetAnswerTheoryResponse(answer=long_answer, type="long").json().encode("utf-8") + b"\n\n"
#
#     return StreamingResponse(answer_stream(), media_type="application/json")
