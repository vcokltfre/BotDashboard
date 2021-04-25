from os import getenv
from dataclasses import dataclass, field

from pydantic import BaseModel
from fastapi.responses import RedirectResponse


class SaveData(BaseModel):
    code: str


@dataclass
class AuthState:
    session: str = field(default=None)
    user: int = field(default=None)

    def authorize(self, after: str) -> RedirectResponse:
        redirect = RedirectResponse(getenv("OAUTH_URI"))
        redirect.set_cookie("oauth_after", after, max_age=60)
        return redirect
