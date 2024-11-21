import asyncio
import os
import sys
from typing import List, Optional

import uvicorn
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from src.models import Employee, WorkloadContainer
from src.routers import load_files_router, employee_router, workload_router, lesson_router, export_router
import ast

app = FastAPI()

app.include_router(load_files_router, prefix='/load')
app.include_router(employee_router, prefix='/employee')
app.include_router(workload_router, prefix='/workload')
app.include_router(lesson_router, prefix='/lesson')
app.include_router(export_router, prefix='/export')

import strawberry
from dependency_injector.wiring import Provide
from fastapi.params import Depends

from src.contaier import MainContainer
from src.graph_ql.types import EmployeeQ, WorkloadContainerQ
from src.services import EmployeeService2

def get_employees_service(employee_service: EmployeeService2 = Depends(Provide[MainContainer.employee_service_2])):
    return employee_service

#Погинация, фильтр по
@strawberry.type
class Query:
    @strawberry.field
    async def employees(self, filters: Optional[str]) -> list[EmployeeQ] | None:
        return await get_employees_service().search(Employee, ast.literal_eval(filters))

    @strawberry.field
    async def workloads(self, filters: Optional[str]) -> list[WorkloadContainerQ] | None:
        return await get_employees_service().search(WorkloadContainer, ast.literal_eval(filters))

# Схема для GraphQL
schema = strawberry.Schema(query=Query)

# Добавление маршрута GraphQL
graphql_app = GraphQLRouter(schema)

# Добавление маршрута в FastAPI
app.include_router(graphql_app, prefix="/graphql")

def add_moules_in_container(container_to_add: MainContainer) -> None:
    excluded_files = ['__init__.py', '__pycache__']
    for file in os.listdir("src/routers"):
        if file in excluded_files: continue
        module = f"src.routers.{file.replace('.py', '')}"
        container_to_add.wire(modules=[sys.modules[module]])
    container_to_add.wire(modules=[sys.modules[__name__]])

    # for file in os.listdir("src/utils"):
    #     if file in excluded_files: continue
    #     module = f"src.utils.{file.replace('.py', '')}"
    #     container_to_add.wire(modules=[sys.modules[module]])
    # container_to_add.wire(modules=[sys.modules[__name__]])


def migrate(container: MainContainer):
    pass


if __name__ == "__main__":
    container = MainContainer()

    add_moules_in_container(container)
    migrate(container=container)

    uvicorn.run(app, host="0.0.0.0", port=container.config().server.port)
