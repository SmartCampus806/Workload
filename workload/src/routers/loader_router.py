from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from src.contaier import MainContainer
from src.services import ParseEmployeeService, ParseEmployeeLessonService, ParseWorkloadService

load_files_router = APIRouter()

@load_files_router.get('/workload')
@inject
async def parse_workload(file: UploadFile = File(...),
                   service: ParseWorkloadService = Depends(Provide[MainContainer.parse_workload_service])):
    # if not file.filename.endswith('.xlsx'):
    #     raise HTTPException(status_code=400, detail='File format not supported. Please upload an .xlsx file')

    content = await file.read()
    await service.parse_and_save_workload(content)
    return "OK"


@load_files_router.get('/employees')
@inject
async def parse_employees(file: UploadFile = File(...),
                   service: ParseEmployeeService = Depends(Provide[MainContainer.parse_employee_service])):
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail='File format not supported. Please upload an .xlsx file')

    contents = await file.read()
    await service.parse(contents)


@load_files_router.get('/employees-lesson')
@inject
async def parse_employees(file: UploadFile = File(...),
                   service: ParseEmployeeLessonService = Depends(Provide[MainContainer.parse_employee_lesson_service])):
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail='File format not supported. Please upload an .xlsx file')

    contents = await file.read()
    await service.parse(contents)
