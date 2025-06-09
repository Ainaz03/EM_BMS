from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.routers.auth import router as auth_router
from app.routers.meetings import router as meetings_router
from app.routers.tasks import router as tasks_router
from app.routers.teams import router as teams_router
from app.routers.calendar import router as calendar_router
from app.admin_panel.admin import setup_admin


app = FastAPI(
    title="Business Management System"
)

app.include_router(auth_router)
app.include_router(meetings_router)
app.include_router(tasks_router)
app.include_router(teams_router)
app.include_router(calendar_router)

setup_admin(app)

@app.get("/")
def root():
    return {"message": "Welcome to the Business Management System API"}
