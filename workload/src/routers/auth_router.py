from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from src.contaier import MainContainer
from src.services.workload_service import WorkloadService

load_files_router = APIRouter()

@load_files_router.get('/')
@inject
async def register(service: WorkloadService = Depends(Provide[MainContainer.workload_service])):
    await service.test()
    return "OK"

