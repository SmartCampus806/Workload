from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, UploadFile, File
from starlette.responses import FileResponse

from src.contaier import MainContainer
from src.services import ExportService

export_router = APIRouter()

@export_router.get('/lessons')
@inject
async def parse_workload(service: ExportService = Depends(Provide[MainContainer.export_service])):
        file_path = await service.export_lessons()

        return FileResponse(
            path=file_path,
            filename="lectures.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

@export_router.get('/lessons-unique')
@inject
async def parse_workload(service: ExportService = Depends(Provide[MainContainer.export_service])):
        file_path = await service.export_unique_lessons()

        return FileResponse(
            path=file_path,
            filename="lectures-unique.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

@export_router.get('/worklaods')
@inject
async def parse_workload(service: ExportService = Depends(Provide[MainContainer.export_service])):
        file_path = await service.export_workload()

        return FileResponse(
            path=file_path,
            filename="worklaods.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
