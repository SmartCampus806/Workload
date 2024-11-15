from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from src.contaier import MainContainer
from src.services import EmployeeService
from src.services.parse_workload_service import ParseWorkloadService

load_files_router = APIRouter()

@load_files_router.get('/workload')
@inject
async def register(file: UploadFile = File(...),
                   service: ParseWorkloadService = Depends(Provide[MainContainer.parse_workload_service])):
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail='File format not supported. Please upload an .xlsx file')

    content = await file.read()
    await service.parse_and_save_workload(content)
    return "OK"


@load_files_router.get('/employees')
@inject
async def register(file: UploadFile = File(...),
                   service: EmployeeService = Depends(Provide[MainContainer.employee_service])):
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail='File format not supported. Please upload an .xlsx file')

    contents = await file.read()
    service.parse_and_save_employees(contents)
