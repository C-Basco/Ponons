from pydantic import BaseModel
from typing import List, Union, Optional
import json
from queries.pool import pool


class Error(BaseModel):
    message: str


class Members(BaseModel):
    user_id: int


class ProjectIn(BaseModel):
    title: str
    description: str
    owner_id: int
    member: Optional[Members]


class ProjectOut(BaseModel):
    id: int
    title: str
    description: str
    owner_id: int
    member: Optional[Members]


class ProjectRepository(BaseModel):
    def get_one(self, project_id: int) -> Optional[ProjectOut]:
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    result = db.execute(
                        """
                        SELECT id
                            , title
                            , description
                            , owner_id
                            , member
                        FROM projects
                        WHERE id = %s
                        """,
                        [project_id]
                    )
                    record = result.fetchone()
                    if record is None:
                        return None
                    return self.record_to_project_out(record)
        except Exception as e:
            print(e)
            return {"message": "Unable to retrieve project"}

    def delete(self, project_id: int) -> bool:
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    db.execute(
                        """
                        DELETE FROM projects
                        WHERE id = %s
                        """,
                        [project_id]
                    )
                    return True
        except Exception as e:
            print(e)
            return False

    def update(self, project_id: int, project: ProjectIn) -> Union[ProjectOut, Error]:
        try:
            with pool.conncetion() as conn:
                with conn.cursor() as db:
                    db.execute(
                        """
                        UPDATE projects
                        SET title = %s
                        , description = %s
                        , owner_id = %s
                        , member = %s
                        WHERE id = %s
                        """,
                        [
                            project.title,
                            project.description,
                            project.owner_id,
                            project.member,
                            project_id
                        ]
                    )
                    return self.project_in_to_out(project_id, project)
        except Exception as e:
            print(e)
            return {"message": "Unable to update project"}

    def get_all(self) -> Union[List[ProjectOut], Error]:
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    db.execute(
                        """
                        SELECT id, title, description, owner_id, member
                        FROM projects;
                        """
                    )
                    return [
                        ProjectOut(
                            id=record[0],
                            title=record[1],
                            description=record[2],
                            owner_id=record[3],
                            member=record[4],
                        )
                        for record in db
                    ]
        except Exception:
            return {"message": "Unable to retrieve a list of projects"}

    def create(self, project: ProjectIn) -> ProjectOut:
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    result = db.execute(
                        """
                        INSERT INTO projects
                            (title, description, owner_id, member)
                        VALUES
                            (%s, %s, %s, %s)
                        RETURNING id;
                        """,
                        [
                            project.title,
                            project.description,
                            project.owner_id,
                            project.member,
                        ]
                    )
                    id = result.fetchone()[0]
                    return self.project_in_to_out(id, project)
        except Exception as e:
            print(e)
            return {"message": "Unable to create project"}

    def project_in_to_out(self, id: int, project: ProjectIn):
        old_data = project.dict()
        return ProjectOut(id=id, **old_data)

    def record_to_project_out(self, record):
        return ProjectOut(
            id=record[0],
            title=record[1],
            description=record[2],
            owner_id=record[3],
            member=record[4],
        )
