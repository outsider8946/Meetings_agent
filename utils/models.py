from typing import Optional, List, Dict, TypedDict, Any
from pydantic import BaseModel, Field, field_validator


class AgentState(TypedDict):
    input: Optional[str] # agent input
    dialog: Optional[str] # dialog for analys
    names: Optional[List[str]] # dialog participants
    classify_result: Optional[str] # result of classify user query
    users: Optional[List[Dict[str,str]]] # users name with jira id
    accounts: Optional[Dict[str, str]] # jira's accounts of current project
    extracted_tasks: Optional[Dict[str, str]] # tasks, extracted from dialog
    summary: Optional[str] # dialog summary 
    feedback: Optional[str] # feedback by agent output
    report: Optional[str] # agent output
    jira_tasks: Optional[List[Dict[str,str]]] # tasks from jira
    matched_tasks: Optional[List[Dict[str, str]]] # task matched from jira and dialog


class ClassifyValidator(BaseModel):
    result: str = Field(..., description="Строго один из вариантов 'valid dialog', 'unvalid dialog', 'not dialog'")

    @field_validator('result')
    def validate_result(cls, value: str) -> str:
        if value not in {'valid dialog', 'unvalid dialog', 'jira', 'query'}:
            value = 'unvalid dialog'

        return value.strip()


class TaskValidator(BaseModel):
    result: List[Dict[str, str]] = Field(
        ..., 
        description="Список json объектов с ключами 'reporter' (создатель здачи), 'assigned' (исполнитель задачи), 'description' (описание задачи), 'name' (название задачи)")

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


class MatchTaskValidator(BaseModel):
    result: Dict[str, List[Dict[str, str]]] = Field(
        ...,
        description="Словарь с ключами 'updated_tasks', 'new_tasks', 'unchanged_tasks'"
    )

    @field_validator('result')
    def validate_result(cls, value: Any) -> Dict[str, List[Dict[str, str]]]:
        expected_top_keys = {'updated_tasks', 'new_tasks', 'unchanged_tasks'}
        if not isinstance(value, dict):
            return {key: [] for key in expected_top_keys}

        normalized_result = {}

        for key in expected_top_keys:
            task_list = value.get(key, [])
            if not isinstance(task_list, list):
                normalized_result[key] = []
                continue

            normalized_tasks = []
            for item in task_list:
                if not isinstance(item, dict):
                    # Полная заглушка
                    normalized_tasks.append({
                        'id': '', 'name': '', 'description': '', 'reporter': '', 'assigned': ''
                    })
                    continue

                # Определяем, какие ключи ожидаем
                if key == 'new_tasks':
                    # id не обязателен в исходных данных
                    expected_keys = {'name', 'description', 'reporter', 'assigned'}
                    # Но в результате всё равно возвращаем id (пустой)
                    if not expected_keys.issubset(item.keys()):
                        normalized_tasks.append({
                            'id': '', 'name': '', 'description': '', 'reporter': '', 'assigned': ''
                        })
                    else:
                        normalized_tasks.append({
                            'id': str(item.get('id', '') or ''),
                            'name': str(item['name']),
                            'description': str(item['description']),
                            'reporter': str(item['reporter']),
                            'assigned': str(item['assigned'])
                        })
                else:
                    # Для updated/unchanged — все 5 полей обязательны
                    expected_keys = {'id', 'name', 'description', 'reporter', 'assigned'}
                    if set(item.keys()) != expected_keys:
                        normalized_tasks.append({
                            'id': '', 'name': '', 'description': '', 'reporter': '', 'assigned': ''
                        })
                    else:
                        normalized_tasks.append({
                            'id': str(item['id']),
                            'name': str(item['name']),
                            'description': str(item['description']),
                            'reporter': str(item['reporter']),
                            'assigned': str(item['assigned'])
                        })

            normalized_result[key] = normalized_tasks

        return normalized_result


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


class CreateTaskInputSchema(BaseModel):
    """Используй эту функцию, если нужно создать задачу из диалога в Jira проетке"""
    summary: str = Field(..., description="Краткое содержание задачи")
    description: str = Field(..., description="Подробное описание задачи")
    assigned_id: str = Field(..., description="Индентификатор исполнителя задачи")
    reported_id: str = Field(..., description="Индентификатор создателя задачи")


class CheckDialogInputSchema(BaseModel):
    """Используй эту функцию, если нужно проверить диалог на корректность"""
    dialog: str = Field(..., description="Диалог")