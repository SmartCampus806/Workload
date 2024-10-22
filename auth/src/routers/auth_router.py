import bcrypt
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException

from src.contaier import MainContainer
from src.dtos import UserCreate, TokenRefreshRequest
from src.exceptions import MyException
from src.models.user import UserRole
from src.services import AuthService
from src.utils.get_user import has_access

auth_router = APIRouter()


@auth_router.get('/register')
@inject
async def register(user: UserCreate,
                   service: AuthService = Depends(Provide[MainContainer.auth_service])):
    user.password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    try:
        return await service.register_user(user)
    except MyException as ex:
        raise HTTPException(status_code=400, detail=ex.get_msg())


@auth_router.get('/login')
@inject
async def register(user: UserCreate,
                   service: AuthService = Depends(Provide[MainContainer.auth_service])):
    result = await service.login(user.email, user.password)
    if result is None:
        raise HTTPException(status_code=400, detail="Password or login incorrect")
    return result


@auth_router.get('/refresh')
@inject
async def refresh(token: TokenRefreshRequest,
                  service: AuthService = Depends(Provide[MainContainer.auth_service])):
    return await service.refresh(token.refresh_token)


@auth_router.get('/logout')
@has_access(roles=[UserRole.load_service.value])
@inject
async def logout(user_id, service: AuthService = Depends(Provide[MainContainer.auth_service])):
    return "Logout success"


@auth_router.get('/test')
@has_access(roles=[UserRole.load_service.value])
async def test_jwt(user_id):
    return f'Hello: {user_id}'
