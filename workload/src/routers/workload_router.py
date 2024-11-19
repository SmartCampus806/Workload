from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException

from src.services import WorkloadService
from src.contaier import MainContainer
from src.dtos.employees import EmployeeDTO, WorkloadDTO
from src.dtos.create_dtos import CreateWorkload
from src.exceptions import (UniqueConstraintViolationException, NotNullConstraintViolationException,
                            ForeignKeyViolationException)
from src.exceptions.all_exceptions import GroupNotFound
from src.services.workload_service2 import WorkloadService2

workload_router = APIRouter()


@workload_router.get('/create', response_model=WorkloadDTO)
@inject
async def create(workload: CreateWorkload,
                 service: WorkloadService2 = Depends(Provide[MainContainer.workload_service2])) -> EmployeeDTO:
    try:
        return await service.create_workload(workload)
    except UniqueConstraintViolationException as ex:
        raise HTTPException(status_code=400, detail='Нагрузка уже существует, проверьте правильность введенного имени')
    except NotNullConstraintViolationException as ex:
        raise HTTPException(status_code=400,
                            detail='Не все обязательные поля введены, обратитесь в поддержку или проверьте введнные поля')
    except GroupNotFound as ex:
        raise HTTPException(status_code=400, detail='Группа не найдена')
    except ForeignKeyViolationException as ex:
        raise HTTPException(status_code=400, detail='Не удалось установить связи между нагрузкой и преподавателем или предметом, обратитесть в поддержку')


@workload_router.get('/')
@inject
async def create(service: WorkloadService = Depends(Provide[MainContainer.workload_service])):
    return await service.get_workload_containers()