import asyncio
import os
import sys
from typing import List, Optional

import uvicorn
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from src.models import Employee, WorkloadContainer
from src.routers import load_files_router, export_router
import ast
from src.services import FilterService

app = FastAPI()

app.include_router(load_files_router, prefix='/load')
app.include_router(export_router, prefix='/export')

import strawberry
from dependency_injector.wiring import Provide
from fastapi.params import Depends

from src.contaier import MainContainer
from src.graph_ql.types import EmployeeQ, WorkloadContainerQ


def get_filter_service(filter_service: FilterService = Depends(Provide[MainContainer.filter_service])) -> FilterService:
    return filter_service



@strawberry.type
class Query:

    @strawberry.field
    async def employees_v2(self, filters: Optional[str], sort_field: Optional[str]) -> list[EmployeeQ]:
        return await get_filter_service().search(model=Employee,filters=ast.literal_eval(filters),
                                                 sort_by=(sort_field, 'asc'))

    @strawberry.field
    async def workloads(self, filters: Optional[str], sort_field: Optional[str]) -> list[WorkloadContainerQ]:
        return await get_filter_service().search(model=WorkloadContainer,filters=ast.literal_eval(filters),
                                                 sort_by=(sort_field, 'asc') )


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
