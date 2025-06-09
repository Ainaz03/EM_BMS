# app/admin/__init__.py

from sqladmin import Admin
from app.core.database import engine
from app.admin_panel.views import TeamAdmin, UserAdmin, TaskAdmin, MeetingAdmin, CommentAdmin, EvaluationAdmin


# Добавляем в FastAPI-приложение
def setup_admin(app):
    admin = Admin(app, engine)
    admin.add_view(UserAdmin)
    admin.add_view(TeamAdmin)
    admin.add_view(TaskAdmin)
    admin.add_view(MeetingAdmin)
    admin.add_view(CommentAdmin)
    admin.add_view(EvaluationAdmin)
