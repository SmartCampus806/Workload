import strawberry
from dependency_injector.wiring import Provide
from fastapi.params import Depends

from contaier import MainContainer
from graph_ql.types import EmployeeQ
from services import EmployeeService


@strawberry.type
class Query:
    @strawberry.field
    async def employees(self, employee_service: EmployeeService = Depends(
                   Provide[MainContainer.employee_service])) -> list[EmployeeQ]:
        return await employee_service.get_all()