from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.meetings import router as meetings_router
from app.routers.tasks import router as tasks_router
from app.routers.teams import router as teams_router


app = FastAPI(
    title="Business Management System"
)

app.include_router(auth_router, prefix="/api")
app.include_router(meetings_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")
app.include_router(teams_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Welcome to the Business Management System API"}
