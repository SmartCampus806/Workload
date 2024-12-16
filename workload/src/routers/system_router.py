from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from src.contaier import MainContainer
from src.services import AllocationService

system_router = APIRouter()

@system_router.get('/allocate')
@inject
async def parse_workload(service: AllocationService = Depends(Provide[MainContainer.allocation_service])):
    await service.distribute_workload()
    return "OK"

@system_router.get('/allocate-genetic')
@inject
async def parse_workload(service: AllocationService = Depends(Provide[MainContainer.allocation_service])):
    await service.distribute_workload_with_genetic()
    return "OK"

@system_router.get('/clear-allocate')
@inject
async def parse_workload(service: AllocationService = Depends(Provide[MainContainer.allocation_service])):
    await service.remove_allocation()
    return "OK"