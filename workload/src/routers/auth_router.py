import bcrypt
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException

from src.contaier import MainContainer
from src.utils.get_user import has_access

load_files_router = APIRouter()

