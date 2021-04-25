from typing import Union

from fastapi import Request, Response
from fastapi.routing import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse

from secrets import token_hex
from itsdangerous import URLSafeSerializer

from src.oauth import build_oauth_token_request


router = APIRouter()
auth_s = URLSafeSerializer(token_hex(32))


@router.get("/callback", include_in_schema=False)
async def auth_callback(request: Request) -> Response:
    """
    Create the user given the authorization code and output the token.
    This endpoint is only used as a redirect target from discord.
    """
    code = request.query_params["code"]
    try:
        token_params, token_headers = build_oauth_token_request(code)
        token = await (await request.state.session.post("https://discord.com/api/oauth2/token", data=token_params, headers=token_headers)).json()
        auth_header = {"Authorization": f"Bearer {token['access_token']}"}
        user = await (await request.state.session.get("https://discord.com/api/users/@me", headers=auth_header)).json()
    except KeyError:
        raise HTTPException(401, "Unknown error while creating token")

    token = auth_s.dumps(token)
    redirect = RedirectResponse(request.cookies.get("oauth_after", "/"), status_code=303)
    await request.state.db.create_session(token, int(user["id"]))
    redirect.set_cookie("session_token", token)
    return redirect
