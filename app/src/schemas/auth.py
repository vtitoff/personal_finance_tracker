from pydantic import BaseModel


class AuthOutputSchema(BaseModel):
    access_token: str
    refresh_token: str
