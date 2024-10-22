from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str


class TokenData(BaseModel):
    sub: str


class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str


class UserDto(UserCreate):
    id: int


class TokenRefreshRequest(BaseModel):
    refresh_token: str
