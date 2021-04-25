from os import getenv

from fastapi import Request, Response
from fastapi.routing import APIRouter
from fastapi.exceptions import HTTPException

from src.models import BotCreateData, ConfigCreateData


router = APIRouter(prefix="/api")

def verify(request: Request) -> None:
    if request.headers.get("X-Api-Token", None) != getenv("API_TOKEN"):
        raise HTTPException(401)

@router.post("/bots/{botid}")
async def create_bot(botid: int, data: BotCreateData, request: Request) -> Response:
    """Create a new bot."""

    verify(request)

    await request.state.db.api_create_bot(botid, data.name)

    return Response(status_code=202)

@router.delete("/bots/{botid}")
async def delete_bot(botid: int, request: Request) -> Response:
    """Delete a bot."""

    verify(request)

    await request.state.db.api_delete_bot(botid)

    return Response(status_code=204)

@router.post("/configs/{guildid}/{botid}")
async def create_config(guildid: int, botid: int, data: ConfigCreateData, request: Request) -> Response:
    """Create a new bot config."""

    verify(request)

    try:
        await request.state.db.api_create_config(guildid, botid, data.guildname, data.config)
    except:
        raise HTTPException(400, "Bot doesn't exist.")

    return Response(status_code=202)

@router.delete("/configs/{guildid}/{botid}")
async def delete_config(guildid: int, botid: int, request: Request) -> Response:
    """Create a new bot config."""

    verify(request)

    await request.state.db.api_delete_config(guildid, botid)

    return Response(status_code=204)
