from typing import Dict
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from utils.jira_api import get_users, create_task


class CreateTaskInputSchema(BaseModel):
    """Используй эту функцию, если нужно создать задачу из диалога в Jira проетке"""
    summary: str = Field(..., description="Краткое содержание задачи")
    description: str = Field(..., description="Подробное описание задачи")
    assigned_id: str = Field(..., description="Индентификатор исполнителя задачи")
    reported_id: str = Field(..., description="Индентификатор создателя задачи")

class CheckDialogInputSchema(BaseModel):
    """Используй эту функцию, если нужно проверить диалог на корректность"""
    dialog: str = Field(..., description="Диалог")


@tool("get_users_tool", description="Используй эту функцию, если нужно получать имена пользователей и их индентификаторы""")
def get_users_tool() -> Dict:
    return get_users()


@tool("create_task_tool",args_schema=CreateTaskInputSchema)
def create_task_tool(summary: str, description: str, assigned_id: str, reporter_id: str) -> Dict:
    return create_task(summary, description, assigned_id, reporter_id)


tools = [get_users_tool, create_task_tool]