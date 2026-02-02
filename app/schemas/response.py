from typing import List

from pydantic import BaseModel, Field


class Reason(BaseModel):
    source: str
    note: str


class AnalyzeResponse(BaseModel):
    risk_stage: str = Field(..., description="normal | suspicious | critical")
    type: str
    reason: List[Reason] = Field(default_factory=list)
    summary: str
    recommended_questions: List[str]
