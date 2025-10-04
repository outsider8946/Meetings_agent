from typing import Optional, List, Dict, TypedDict
from pydantic import BaseModel, Field, field_validator


class AgentState(TypedDict):
    input: Optional[str] # agent input
    dialog: Optional[str] # dialog for analys
    names: Optional[List[str]] # dialog participants
    validate_result: Optional[str] # result of dialog validate
    users: Optional[List[Dict[str,str]]] # users name with jira id
    accounts: Optional[Dict[str, str]] # jira's accounts of current project
    extracted_tasks: Optional[Dict[str, str]] # tasks, extracted from dialog
    summary: Optional[str] # dialog summary 
    feedback: Optional[str] # feedback by agent output
    report: Optional[str] # agent output
    jira_tasks: Optional[List[Dict[str,str]]] # tasks from jira
    matched_tasks: Optional[List[Dict[str, str]]] # task matched from jira and dialog


class DialogValidator(BaseModel):
    result: str = Field(..., description="Строго один из вариантов 'valid dialog', 'unvalid dialog', 'not dialog'")

    @field_validator('result')
    def validate_result(cls, value: str) -> str:
        if value not in {'valid dialog', 'unvalid dialog', 'jira', 'query'}:
            value = 'unvalid dialog'

        return value.strip()


class TaskValidator(BaseModel):
    result: List[Dict[str, str]] = Field(..., description="Список json объектов с ключами 'reporter' (создатель здачи), 'assigned' (исполнитель задачи), 'description' (описание задачи), 'name' (название задачи)")

    @field_validator('result')
    def validate_result(cls, value) -> List[Dict[str, str]]:
        result_value = []
        for item in value:
            if not isinstance(item, Dict):
                result_value.append({'reporter':'', 'assigned': '', 'description':'', 'name':''})
            elif set(item.keys()) != {'reporter', 'assigned', 'description', 'name'}:
                result_value.append({'reporter':'', 'assigned': '', 'description':'', 'name':''})
            else:
                result_value.append(item)
        
        return result_value


class UserValidator(BaseModel):
    result: List[Dict[str, str]] = Field(..., description="Список json объектов с ключами 'name' (имя) и 'id' (идентификатор аккаунта)")

    @field_validator('result')
    def validate_result(cls, value) -> List[Dict[str, str]]:
        result_value = []

        for item in value:
            if not isinstance(item, Dict):
                result_value.append({'name':'', 'id':''})
            elif set(item.keys()) != {'name', 'id'}:
                result_value.append({'name':'', 'id':''})
            else:
                result_value.append(item)
        
        return result_value