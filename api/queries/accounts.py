from pydantic import BaseModel
from typing import List, Union
from queries.pool import pool


class Error(BaseModel):
    message: str


class DuplicateAccountError(ValueError):
    pass


class UsersIn(BaseModel):
    username: str
    first: str
    last: str
    email: str
    password: str


class UsersOut(BaseModel):
    id: int
    username: str
    first: str
    last: str
    email: str


class UsersHashedPassword(UsersOut):
    hashed_password: str


class AccountsRepo(BaseModel):
    def get(self, username: str) -> UsersHashedPassword:
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    result = db.execute(
                        """
                        SELECT id
                        , username
                        , first
                        , last
                        , email
                        , hashed_password
                        FROM users
                        WHERE username = %s;
                        """,
                        [username]
                    )
                    record = result.fetchone()
                    return self.record_to_user_out_with_hash(record)
        except Exception as e:
            print(e)
            return {"message": "Unable to retrtieve user"}

    # def delete(self, user_id: int) -> bool:
    #     try:
    #         with pool.connection as conn:
    #             with conn.cursor() as db:
    #                 db.execute(
    #                     """
    #                     DELETE FROM users
    #                     WHERE id = %s;
    #                     """,
    #                     [user_id]
    #                 )
    #                 return True
    #     except Exception as e:
    #         print(e)
    #         return False

    # def update(self, user_id: int, user: UsersIn) -> Union[UsersOut, Error]:
    #     try:
    #         with pool.connection() as conn:
    #             with conn.cursor() as db:
    #                 db.execute(
    #                     """
    #                     UPDATE users
    #                     SET username = %s
    #                         ,first = %s
    #                         , last = %s
    #                         , email = %s
    #                         , hashed_password = %s
    #                     WHERE id = %s
    #                     """,
    #                     [user.username,
    #                      user.first,
    #                      user.last,
    #                      user.email,
    #                      user.password,
    #                      ]
    #                 )
    #                 return self.user_in_to_out(user_id, user)
    #     except Exception as e:
    #         print(e)
    #         return {"message": "Unable to update user"}

    def get_all(self) -> Union[List[UsersOut], Error]:
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    db.execute(
                        """
                        SELECT id
                            , username
                            , first
                            , last
                            , email
                        FROM users
                        """,
                    )
                    return [
                        UsersOut(
                            id=record[0],
                            username=record[1],
                            first=record[2],
                            last=record[3],
                            email=record[4],
                        )
                        for record in db
                    ]
        except Exception as e:
            print(e)
            return {"message": "Unable to retrieve list of users"}

    def create(
            self, info: UsersIn, hashed_password: str
    ) -> UsersHashedPassword:
        with pool.connection() as conn:
            with conn.cursor() as db:
                result = db.execute(
                    """
                    INSERT INTO users
                        (username, first, last, email, hashed_password)
                    VALUES
                        (%s, %s, %s, %s, %s)
                    RETURNING id, username, first, last, email, hashed_password;
                    """,
                    [info.username,
                     info.first,
                     info.last,
                     info.email,
                     hashed_password]
                )
                record = result.fetchone()
                if record is None:
                    return None
                return self.record_to_user_out_with_hash(record)

    def user_in_to_out(self, id, account: UsersIn):
        old_data = account.model_dump()
        return UsersHashedPassword(id=id, **old_data)

    def record_to_user_out(self, record):
        return UsersOut(
            id=record[0],
            username=record[1],
            first=record[2],
            last=record[3],
            email=record[4],
            password=record[5],
        )

    def record_to_user_out_with_hash(self, record):
        return UsersHashedPassword(
            id=record[0],
            username=record[1],
            first=record[2],
            last=record[3],
            email=record[4],
            hashed_password=record[5],
        )
