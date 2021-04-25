from dataclasses import dataclass, field

from pydantic import BaseModel


class SaveData(BaseModel):
    code: str


@dataclass
class AuthState:
    session: str = field(default=None)
    user: int = field(default=None)
