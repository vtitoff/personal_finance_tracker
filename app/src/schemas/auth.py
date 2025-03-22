from pydantic import BaseModel


class BaseAuthSchema(BaseModel):
    access_token: str
    refresh_token: str


class AuthOutputSchema(BaseAuthSchema):
    pass


class RefreshInputSchema(BaseAuthSchema):
    pass


class LoginInputSchema(BaseModel):
    login: str
    password: str
