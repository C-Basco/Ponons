from authenticator import authenticator
from routers import (
    projects,
    accounts,
    tasks,
)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()
app.include_router(authenticator.router)
app.include_router(projects.router)
app.include_router(accounts.router)
app.include_router(tasks.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.environ.get("CORS_HOST", "http://localhost:3000")
        ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
