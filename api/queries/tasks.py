from pydantic import BaseModel
from datetime import date
from typing import List, Union, Optional
from queries.pool import pool


class Error(BaseModel):
    message: str


class Assignees(BaseModel):
    assignee_id: int


class Projects(BaseModel):
    project_id: int


class TaskIn(BaseModel):
    name: str
    start_date: date
    due_date: date
    is_completed: int
    project: Projects
    assignee: Optional[Assignees]


class TaskOut(BaseModel):
    id: int
    name: str
    start_date: date
    due_date: date
    is_completed: int
    project: Projects
    assignee: Assignees


class TasksRepository(BaseModel):
    def get_one(self, task_id: int) -> Optional[TaskOut]:
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    result = db.execute(
                        """
                        SELECT id
                            , name
                            , start_date
                            , due_date
                            , is_completed
                            , project_id
                            , assignee
                        FROM tasks
                        WHERE id = %s
                        """,
                        [task_id]
                    )
                    record = result.fetchone()
                    if record is None:
                        return None
                    return self.record_to_task_out(record)
        except Exception as e:
            print(e)
            return {"message": "Unable to retrieve task"}

    def delete(self, task_id: int) -> bool:
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    db.execute(
                        """
                        DELETE FROM tasks
                        WHERE id=%s
                        """,
                        [task_id]
                    )
                    return True
        except Exception as e:
            print(e)
            return False

    def update(self, task_id: int, task: TaskIn) -> Union[TaskOut, Error]:
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    db.execute(
                        """
                        UPDATE tasks
                        SET name = %s
                            , start_date = %s
                            , due_date = %s
                            , is_completed = %s
                            , project = %s
                            , assignee = %s
                        WHERE id = %s
                        """,
                        [
                            task.name,
                            task.start_date,
                            task.due_date,
                            task.is_completed,
                            task.project,
                            task.assignee,
                        ]
                    )
                    return self.task_in_to_out(id, task)
        except Exception as e:
            print(e)
            return {"message": "Unable to update task"}

    def get_all(self) -> Union[List[TaskOut], Error]:
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    db.execute(
                        """
                        SELECT id, name, start_date, due_date, is_completed, project_id, assignee
                        FROM tasks;
                        """,
                    )
                    return [self.record_to_task_out(record) for record in db]
        except Exception as e:
            print(e)
            return {"message": "Unable to retrieve list of tasks"}

    def create(self, task: TaskIn) -> TaskOut:
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    result = db.execute(
                        """
                        INSERT INTO tasks
                            (name, start_date, due_date, is_completed, project_id, assignee)
                        VALUES
                            (%s, %s, %s, %s, %s, %s)
                        RETURNING id;
                        """,
                        [
                            task.name,
                            task.start_date,
                            task.due_date,
                            task.is_completed,
                            task.project.project_id,
                            task.assignee.assignee_id,
                        ]
                    )
                    id = result.fetchone()[0]
                    return self.task_in_to_out(id, task)
        except Exception as e:
            print(e)
            return {"message": "Unable to create task"}

    def task_in_to_out(self, id, task: TaskIn):
        old_data = task.model_dump()
        return TaskOut(id=id, **old_data)

    def record_to_task_out(self, record):
        return TaskOut(
            id=record[0],
            name=record[1],
            start_date=record[2],
            due_date=record[3],
            is_completed=record[4],
            project=record[5],
            assignee=record[6],
        )
