from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ConversationTurn(BaseModel):
    speaker: Literal["user", "other"] = Field(..., description="Message speaker")
    text: str = Field(..., description="Message content")


class AnalyzeRequest(BaseModel):
    conversation: List[ConversationTurn] = Field(
        ..., description="Ordered conversation turns with speaker and text"
    )
    language: Optional[str] = Field(default=None, description="Optional language hint")
