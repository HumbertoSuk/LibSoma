from pydantic import BaseModel


class InvalidatedToken(BaseModel):
    token: str
