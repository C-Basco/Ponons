# router.py
from fastapi import (
    Depends,
    HTTPException,
    status,
    Response,
    APIRouter,
    Request,
)
from typing import List, Union
from jwtdown_fastapi.authentication import Token
from authenticator import authenticator

from pydantic import BaseModel

from queries.accounts import (
    UsersIn,
    UsersOut,
    AccountsRepo,
    DuplicateAccountError,
    UsersHashedPassword,
    Error
)


class AccountForm(BaseModel):
    username: str
    first: str
    last: str
    email: str
    password: str


class AccountToken(Token):
    account: UsersOut


class HttpError(BaseModel):
    detail: str


router = APIRouter()


@router.get("/token", response_model=AccountToken | None)
async def get_token(
    request: Request,
    account: UsersOut = Depends(authenticator.try_get_current_account_data)
) -> AccountToken | None:
    if account and authenticator.cookie_name in request.cookies:
        return {
            "access_token": request.cookies[authenticator.cookie_name],
            "type": "Bearer",
            "account": account,
        }


@router.post("/api/things")
async def create_thing(
    account_data: dict = Depends(authenticator.get_current_account_data),
):
    pass


@router.post("/api/accounts", response_model=AccountToken | HttpError)
async def create_account(
    info: UsersIn,
    request: Request,
    response: Response,
    repo: AccountsRepo = Depends(),
):
    hashed_password = authenticator.hash_password(info.password)
    try:
        account = repo.create(info, hashed_password)
    except DuplicateAccountError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create an account with those credentials",
        )
    form = AccountForm(
        username=info.username,
        first=info.first,
        last=info.last,
        email=info.email,
        password=info.password
        )
    token = await authenticator.login(response, request, form, repo)
    return AccountToken(account=account, **token.dict())


@router.get("/api/accounts", response_model=Union[List[UsersOut], Error])
def get_all(
    repo: AccountsRepo = Depends(),
):
    return repo.get_all()
