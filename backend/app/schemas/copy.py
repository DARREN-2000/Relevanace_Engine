"""Pydantic schemas for Copy endpoints."""

from pydantic import BaseModel


class CopyGenerateRequest(BaseModel):
    context: dict
    tone: str = "professional"
    objective: str = "educate"
