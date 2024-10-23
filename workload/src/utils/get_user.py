import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from src.contaier import MainContainer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def has_access(roles):
    def jwt_required(func):
        async def wrapper(token: str = Depends(oauth2_scheme)):
            try:
                data = jwt.decode(token, MainContainer.config().jwt.secret,
                                  algorithms=[MainContainer.config().jwt.algorithm])
                if data['role'] not in roles:
                    raise HTTPException(
                        status_code=401,
                        detail="Permission denied",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                return await func(user_id=data['sub'])
            except jwt.PyJWTError:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        return wrapper

    return jwt_required


def has_access_without_user(roles):
    def jwt_required(func):
        async def wrapper(token: str = Depends(oauth2_scheme)):
            try:
                print(type(token), roles)
                data = jwt.decode(token, MainContainer.config().jwt.secret,
                                  algorithms=[MainContainer.config().jwt.algorithm])
                if data['role'] not in roles:
                    raise HTTPException(
                        status_code=401,
                        detail="Permission denied",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                return await func()
            except jwt.PyJWTError:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        return wrapper

    return jwt_required
