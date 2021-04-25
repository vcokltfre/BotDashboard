from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles

from dotenv import load_dotenv
from aiohttp import ClientSession

from src.database import Database
from src.models import AuthState
from src.routers import dash_router, oauth_router, api_router


load_dotenv()

app = FastAPI(docs_url=None)
app.mount("/static", StaticFiles(directory="static"), "static")
app.include_router(dash_router)
app.include_router(oauth_router)
app.include_router(api_router)

session = ClientSession()
db = Database()


@app.on_event("startup")
async def startup() -> None:
    """Initialise the database and session on startup."""

    await db.setup()

@app.middleware("http")
async def authorize(request: Request, call_next) -> Response:
    """Authorize the request with the database."""

    session_token = request.cookies.get("session_token")
    session_data = await db.get_session(session_token or "")

    if session_data:
        state = AuthState(session_token, session_data["member_id"])
    else:
        state = AuthState()

    request.state.authstate = state

    return await call_next(request)

@app.middleware("http")
async def attach_db_http(request: Request, call_next) -> Response:
    """Attach the database and session objects to the request's state."""

    request.state.db = db
    request.state.session = session

    return await call_next(request)

@app.get("/")
async def ping() -> dict:
    """Get a static ping response to confirm the API is alive."""

    return dict(status="ok")
