from typing import TypedDict, Literal

from pydantic import BaseModel


class TranscriptionResponse(BaseModel):
    transcript: str


class GetAnswerTheoryResponse(BaseModel):
    answer: str
    type: str


class ChatMessage(TypedDict):
    role: Literal["user", "assistant", "system"]
    content: str


class ContextData(BaseModel):
    position: str
    grade: str


class QueryGetAnswerTheoryPayload(BaseModel):
    question: str
    context: ContextData
    model: Literal["gpt_4_1_nano", "gpt_4o_mini", "o4_mini_high", "gpt_4_1"]
