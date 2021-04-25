from pydantic import BaseModel


class SaveData(BaseModel):
    code: str
