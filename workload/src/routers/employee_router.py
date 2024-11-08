from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, HTTPException

from src.contaier import MainContainer
from src.dtos.employees import EmployeeWithWorkloadDTO, EmployeeDTO
from src.dtos.util_dto import CreateEmployee
from src.exceptions import UniqueConstraintViolationException, NotNullConstraintViolationException
from src.models import Employee
from src.services import EmployeeService
from src.utils import map_dto_to_model

employee_router = APIRouter()


@employee_router.get('/create', response_model=EmployeeDTO)
@inject
async def create(employee: CreateEmployee,
                 service: EmployeeService = Depends(Provide[MainContainer.employee_service])) -> EmployeeDTO:
    employee_model = map_dto_to_model(employee, Employee())
    try:
        return await service.create_employee(employee_model)
    except UniqueConstraintViolationException as ex:
        raise HTTPException(status_code=400, detail='Педагог уже существует, проверьте правильность введенного имени')
    except NotNullConstraintViolationException as ex:
        raise HTTPException(status_code=400,
                            detail='Не все обязательные поля введены, обратитесь в поддержку или проверьте введнные поля')


@employee_router.get('/full', response_model= None | List[EmployeeWithWorkloadDTO])
@inject
async def full(id: int = Query(default=None), name: str = Query(default=None),
               service: EmployeeService = Depends(
                   Provide[MainContainer.employee_service])) -> EmployeeWithWorkloadDTO | None | \
                                                                list[EmployeeWithWorkloadDTO]:
    if id is not None:
        res = [await service.get_by_id(id=id)]
    elif name is not None:
        res = await service.get_by_name(name)
    else:
        res = await service.get_all()
    return res


@employee_router.get('/full/q', response_model=EmployeeWithWorkloadDTO | None | List[EmployeeWithWorkloadDTO])
@inject
async def full_q(name: str = Query(default=None),
                 service: EmployeeService = Depends(Provide[MainContainer.employee_service])) -> (
        EmployeeWithWorkloadDTO | None | list[EmployeeWithWorkloadDTO]):
    if name is not None:
        res = await service.get_by_name_like(name)
    else:
        res = await service.get_all()
    return res


@employee_router.get('/', response_model=EmployeeDTO | None | List[EmployeeDTO])
@inject
async def small(id: int = Query(default=None), name: str = Query(default=None),
                service: EmployeeService = Depends(
                    Provide[MainContainer.employee_service])) -> EmployeeDTO | None | \
                                                                 list[EmployeeDTO]:
    if id is not None:
        res = await service.get_by_id(id=id)
    elif name is not None:
        res = await service.get_by_name(name)
    else:
        res = await service.get_all()
    return res


@employee_router.get('/q', response_model=EmployeeDTO | None | List[EmployeeDTO])
@inject
async def small_q(name: str = Query(default=None),
                  service: EmployeeService = Depends(Provide[MainContainer.employee_service])) -> (
        EmployeeDTO | None | list[EmployeeDTO]):
    if name is not None:
        res = await service.get_by_name_like(name)
    else:
        res = await service.get_all()
    return res
