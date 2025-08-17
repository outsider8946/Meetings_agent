from typing import List, Dict
from pydantic import BaseModel, Field, field_validator


class DialogValidator(BaseModel):
    result: str = Field(..., description="Строго один из вариантов 'valid dialog', 'unvalid dialog', 'not dialog'")

    @field_validator('result')
    def validate_result(cls, value: str) -> str:
        if value not in {'valid dialog', 'unvalid dialog', 'not dialog'}:
            value = 'unvalid dialog'

        return value.strip()


class TaskValidator(BaseModel):
    result: List[Dict[str, str]] = Field(..., description="Список json объектов с ключами 'owner' (создатель здачи), 'reported by' (исполнитель задачи), 'task' (задача)")

    @field_validator('result')
    def validate_result(cls, value) -> List[Dict[str, str]]:
        result_value = []
        for item in value:
            if not isinstance(item, Dict):
                result_value.append({'owner':'', 'reported by': '', 'description':'', 'name':''})
            elif set(item.keys()) != {'owner', 'reported by', 'description', 'name'}:
                result_value.append({'owner':'', 'reported by': '', 'description':'', 'name':''})
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