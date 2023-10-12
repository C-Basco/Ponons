from fastapi import APIRouter, Depends, Response
from typing import List, Union, Optional
from queries.projects import (
    Error,
    ProjectIn,
    ProjectOut,
    ProjectRepository
)

router = APIRouter()


@router.post("/projects", response_model=Union[ProjectOut, Error])
def create_project(
    project: ProjectIn,
    response: Response,
    repo: ProjectRepository = Depends()
):
    try:
        return repo.create(project)
    except Exception:
        response.status_code = 400


@router.get("/projects", response_model=Union[List[ProjectOut], Error])
def get_all(
    repo: ProjectRepository = Depends(),
):
    return repo.get_all()


@router.put("/projects/{project_id}", response_model=Union[ProjectOut, Error])
def update_project(
    project_id: int,
    project: ProjectIn,
    repo: ProjectRepository = Depends(),
) -> Union[Error, ProjectOut]:
    return repo.update_project(project_id, project)


@router.delete("/projects/{projects_id}", response_model=bool)
def delete_project(
    project_id: int,
    repo: ProjectRepository = Depends(),
) -> bool:
    return repo.delete(project_id)


@router.get("/project/{project_id}", response_model=Union[Optional[ProjectOut], Error])
def get_one_project(
    project_id: int,
    response: Response,
    repo: ProjectRepository = Depends(),
) -> ProjectOut:
    project = repo.get_one(project_id)
    if project is None:
        response.status_code = 404
    return project
