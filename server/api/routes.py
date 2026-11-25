"""Rutas HTTP del servicio AI Chat Assistant.

Expone la página de inicio y el endpoint ``/chat``. La comunicación con
Ollama se delega en :class:`server.services.ollama.OllamaClient`, inyectado
por FastAPI.
"""
import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from server.config import get_settings
from server.dependencies import OllamaClientDep
from server.schemas.responses import ChatResponse
from server.services.ollama import (
    OllamaClient,
    OllamaRequestError,
    OllamaResponseError,
)

logger = logging.getLogger(__name__)

router = APIRouter()
"""Enrutador con los endpoints públicos del servicio."""


@router.get("/", response_class=FileResponse, summary="Sirve la interfaz web")
def serve_homepage() -> FileResponse:
    """Devuelve el archivo ``static/index.html``.

    :returns: Respuesta con el HTML de la aplicación.
    :rtype: fastapi.responses.FileResponse
    """
    settings = get_settings()
    return FileResponse(settings.static_dir / "index.html")


def _generate_text(client: OllamaClient, prompt: str, fallback: str) -> str:
    """Genera texto y traduce los errores de Ollama a errores HTTP 500.

    :param client: Cliente de Ollama inyectado por FastAPI.
    :type client: server.services.ollama.OllamaClient
    :param prompt: Instrucción completa para el modelo.
    :type prompt: str
    :param fallback: Texto de reserva si la respuesta no trae ``response``.
    :type fallback: str
    :returns: Texto generado por el modelo.
    :rtype: str
    :raises fastapi.HTTPException: Con estado 500 si Ollama no responde o
        devuelve un cuerpo inválido.
    """
    try:
        return client.generate(prompt, fallback)
    except OllamaRequestError as exc:
        logger.error("Fallo al contactar con Ollama: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"Request to Ollama failed: {exc}",
        ) from exc
    except OllamaResponseError as exc:
        logger.error("Respuesta inválida de Ollama: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Responde a un prompt libre",
)
def chat(
    client: OllamaClientDep,
    prompt: Annotated[str, Query(description="Prompt del usuario para el modelo de IA.")],
) -> ChatResponse:
    """Envía un prompt libre al modelo y devuelve su respuesta.

    .. note::
       El prompt se recibe por query string para no romper el frontend
       original. Se documenta como deuda técnica en el README.

    :param client: Cliente de Ollama inyectado por FastAPI.
    :type client: server.services.ollama.OllamaClient
    :param prompt: Texto enviado por el usuario.
    :type prompt: str
    :returns: Respuesta generada por el modelo.
    :rtype: server.schemas.responses.ChatResponse
    :raises fastapi.HTTPException: ``500`` si Ollama no responde o no devuelve
        texto.
    """
    generated = _generate_text(client, prompt, "")
    if not generated:
        raise HTTPException(
            status_code=500,
            detail="No valid response received from Ollama",
        )
    return ChatResponse(response=generated)
