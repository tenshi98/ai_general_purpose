"""Modelo de respuesta de un chat simple."""
from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    """Respuesta generada por el chatbot."""

    response: str = Field(..., description="Respuesta generada por el modelo.")
