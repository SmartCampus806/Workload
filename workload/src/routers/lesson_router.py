from typing import List

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException, Query

from src.contaier import MainContainer
from src.dtos.create_dtos import CreateLesson
from src.dtos.lesson_dtos import SmallLesson, FullLesson
from src.exceptions import UniqueConstraintViolationException, NotNullConstraintViolationException
from src.services import LessonService

lesson_router = APIRouter()


@lesson_router.get('/create', response_model=CreateLesson)
@inject
async def create(dto: CreateLesson,
                 service: LessonService = Depends(Provide[MainContainer.lesson_service])) -> SmallLesson:
    try:
        return await service.create_lesson(dto)
    except UniqueConstraintViolationException as ex:
        raise HTTPException(status_code=400, detail='Педагог уже существует, проверьте правильность введенного имени')
    except NotNullConstraintViolationException as ex:
        raise HTTPException(status_code=400,
                            detail='Не все обязательные поля введены, обратитесь в поддержку или проверьте введнные поля')


@lesson_router.get('/full', response_model=FullLesson | None | list[FullLesson])
@inject
async def full(id: int = Query(default=None), name: str = Query(default=None),
               service: LessonService = Depends(
                   Provide[MainContainer.lesson_service])) -> FullLesson | None | \
                                                              list[FullLesson]:
    if id is not None:
        res = await service.get_by_id(id=id)
    elif name is not None:
        res = await service.get_by_name(name)
    else:
        res = await service.get_all()
    return res


@lesson_router.get('/full/q', response_model=FullLesson | None | list[FullLesson])
@inject
async def full_q(name: str = Query(default=None),
                 service: LessonService = Depends(Provide[MainContainer.lesson_service])) -> (
        FullLesson | None | list[FullLesson]):
    if name is not None:
        res = await service.get_by_name_like(name)
    else:
        res = await service.get_all()
    return res


@lesson_router.get('/', response_model=SmallLesson | None | list[SmallLesson])
@inject
async def small(id: int = Query(default=None), name: str = Query(default=None),
                service: LessonService = Depends(
                    Provide[MainContainer.lesson_service])) -> SmallLesson | None | \
                                                               list[SmallLesson]:
    if id is not None:
        res = await service.get_by_id(id=id)
    elif name is not None:
        res = await service.get_by_name(name)
    else:
        res = await service.get_all()
    return res


@lesson_router.get('/q', response_model=SmallLesson | None | List[SmallLesson])
@inject
async def small_q(name: str = Query(default=None),
                  service: LessonService = Depends(Provide[MainContainer.lesson_service])) -> (
        SmallLesson | None | list[SmallLesson]):
    if name is not None:
        res = await service.get_by_name_like(name)
    else:
        res = await service.get_all()
    return res
