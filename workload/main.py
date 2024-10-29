import os
import sys

import uvicorn
from fastapi import FastAPI

from src.contaier import MainContainer
from src.routers import load_files_router, employee_router, workload_router, lesson_router

app = FastAPI()

app.include_router(load_files_router, prefix='/load')
app.include_router(employee_router, prefix='/employee')
app.include_router(workload_router, prefix='/workload')
app.include_router(lesson_router, prefix='/lesson')


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
