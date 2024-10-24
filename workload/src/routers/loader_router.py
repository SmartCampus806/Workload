import pandas as pd
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from src.contaier import MainContainer
from src.services import EmployeeService
from src.services.workload_service import WorkloadService

load_files_router = APIRouter()


@load_files_router.get('/')
@inject
async def register(service: WorkloadService = Depends(Provide[MainContainer.workload_service])):
    await service.test()
    return "OK"


@load_files_router.get('/workload')
@inject
async def register(file: UploadFile = File(...),
                   service: WorkloadService = Depends(Provide[MainContainer.workload_service])):
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail='File format not supported. Please upload an .xlsx file')

    content = await file.read()
    service.parse_and_save_workload(content)


@load_files_router.get('/employees')
@inject
async def register(file: UploadFile = File(...),
                   service: EmployeeService = Depends(Provide[MainContainer.employee_service])):
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail='File format not supported. Please upload an .xlsx file')

    contents = await file.read()
    service.parse_and_save_employees(contents)
