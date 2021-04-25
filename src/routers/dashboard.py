from typing import Union

from fastapi import Request, Response
from fastapi.routing import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from src.models import SaveData


router = APIRouter(prefix="/config")
templates = Jinja2Templates(directory="templates")


@router.get("/bot/{botid}/guild/{guildid}")
async def dashboard(botid: int, guildid: int, request: Request) -> Union[HTMLResponse, RedirectResponse]:
    """Get the main dashboard page."""

    if not request.state.authstate.user:
        return request.state.authstate.authorize(after=f"/config/bot/{botid}/guild/{guildid}")

    if not await request.state.db.get_access(botid, guildid, request.state.authstate.user):
        raise HTTPException(403, "You are not authorized to access this resource.")

    bot = await request.state.db.get_bot(botid)
    config = await request.state.db.get_config(guildid, botid)

    if not (bot and config):
        return HTTPException(404)

    resp = templates.TemplateResponse("dashboard.html", {
        "request": request,
        "botname": bot["bot_name"],
        "guildname": config["guild_name"],
        "guildid": guildid,
        "botid": botid
    })

    return resp

@router.post("/bot/{botid}/guild/{guildid}")
async def dashboard_save(botid: int, guildid: int, data: SaveData, request: Request) -> HTMLResponse:
    if not request.state.authstate.user:
        raise HTTPException(401, "Not authorized.")

    if not await request.state.db.get_access(botid, guildid, request.state.authstate.user):
        raise HTTPException(403, "You are not authorized to access this resource.")

    await request.state.db.set_config(guildid, botid, data.code)

    return Response(status_code=204)

@router.get("/bot/{botid}/guild/{guildid}/data")
async def get_raw_data(botid: int, guildid: int, request: Request) -> Response:
    if not request.state.authstate.user:
        raise HTTPException(401, "Not authorized.")

    if not await request.state.db.get_access(botid, guildid, request.state.authstate.user):
        raise HTTPException(403, "You are not authorized to access this resource.")

    config = await request.state.db.get_config(guildid, botid)

    return dict(data=config["config"])
