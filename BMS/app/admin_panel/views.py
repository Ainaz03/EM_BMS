# admin_panel/models.py

from sqladmin import ModelView
from app.models.user import User
from app.models.team import Team
from app.models.task import Task, Comment
from app.models.evaluation import Evaluation
from app.models.meeting import Meeting

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.role, User.team_id, User.is_active]
    column_searchable_list = [User.email]
    form_excluded_columns = [
        "hashed_password", "created_tasks", "assigned_tasks",
        "comments", "evaluations", "meetings"
    ]

class TeamAdmin(ModelView, model=Team):
    column_list = [Team.id, Team.name, Team.invite_code, Team.admin_id]
    column_searchable_list = [Team.name]
    form_excluded_columns = ["members"]

class TaskAdmin(ModelView, model=Task):
    column_list = [
        Task.id, Task.title, Task.status,
        Task.creator_id, Task.assignee_id, Task.deadline
    ]
    column_filters = [Task.status]
    form_excluded_columns = ["comments", "evaluations"]

class CommentAdmin(ModelView, model=Comment):
    column_list = [
        Comment.id, Comment.text, Comment.author_id,
        Comment.task_id, Comment.created_at
    ]

class EvaluationAdmin(ModelView, model=Evaluation):
    column_list = [
        Evaluation.id, Evaluation.score,
        Evaluation.evaluator_id, Evaluation.task_id,
        Evaluation.created_at
    ]

class MeetingAdmin(ModelView, model=Meeting):
    column_list = [
        Meeting.id, Meeting.title,
        Meeting.creator_id, Meeting.start_time,
        Meeting.end_time
    ]
    form_excluded_columns = ["participants"]
