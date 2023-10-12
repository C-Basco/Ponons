from fastapi import APIRouter, Depends, Response
from typing import List, Union, Optional
from queries.tasks import (
    Error,
    TaskIn,
    TaskOut,
    TasksRepository,
)

router = APIRouter()


@router.post("/task", response_model=Union[TaskOut, Error])
def create_task(
    task: TaskIn,
    response: Response,
    repo: TasksRepository = Depends(),
):
    response.status_code = 400
    return repo.create(task)


@router.get("/task/{task_id}", response_model=Union[Optional[TaskOut], Error])
def get_one_task(
    task_id: int,
    response: Response,
    repo: TasksRepository = Depends(),
) -> TaskOut:
    task = repo.get_one(task_id)
    if task is None:
        response.status_code = 404
    return task


@router.get("/task", response_model=Union[List[TaskOut], Error])
def get_all_task(
    repo: TasksRepository = Depends(),
):
    return repo.get_all()


@router.put("/task/{task_id}", response_model=Union[TaskOut, Error])
def update_task(
    task_id: int,
    task: TaskIn,
    repo: TasksRepository = Depends(),
) -> Union[TaskOut, Error]:
    return repo.update(task_id, task)


@router.delete("/task/{task_id}", response_model=Union[TaskOut, Error])
def delete_task(
    task_id: int,
    repo: TasksRepository = Depends(),
) -> bool:
    return repo.delete(task_id)
