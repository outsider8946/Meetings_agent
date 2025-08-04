import os
from dotenv import load_dotenv
from typing import List, Dict
from pydantic import SecretStr
from utils.config_loader import config
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field, field_validator
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from utils.templates import SYSTEM_DIALOG_VALIDATE, SYSTEM_MATCH_USERS, SYSTEM_MATCH_USERS, \
                            SYSTEM_TASK_TEMPLATE, SYSTEM_SUMMARY_TEMPLATE

load_dotenv()

class TypeValidator(BaseModel):
    result: str = Field(..., description="Число либо 1, либо 0 без лишних символов")

    @field_validator('result')
    def validate_result(cls, value: str) -> str:
        if value.isdigit():
            if value != '1':
                value = '0'
        else:
            value = '0'

        return value

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



llm = ChatOpenAI(base_url="https://openrouter.ai/api/v1", 
                                api_key=SecretStr(os.environ.get("OPENROUTER_API_KEY") or ""),
                                model=config.llm.model_name,
                                temperature=config.llm.temperature,
                                top_p=config.llm.top_p,
                                default_headers={
                                    "HTTP-Referer": "http://localhost:8501",
                                    "X-Title": "Meetings Agent"
                                }
)


def get_dialog_checker():
    prompt = ChatPromptTemplate.from_template(SYSTEM_DIALOG_VALIDATE)
    llm_with_structed_output = llm.with_structured_output(TypeValidator)
    return RunnablePassthrough() | prompt | llm_with_structed_output

def get_task_extractor():
    prompt = ChatPromptTemplate.from_template(SYSTEM_TASK_TEMPLATE)
    llm_with_structed_output = llm.with_structured_output(TaskValidator)
    return RunnablePassthrough() | prompt | llm_with_structed_output

def get_user_matcher():
    prompt = ChatPromptTemplate.from_template(SYSTEM_MATCH_USERS)
    llm_with_structed_output = llm.with_structured_output(UserValidator)
    return RunnablePassthrough() | prompt | llm_with_structed_output

def get_summarizer():
    prompt = ChatPromptTemplate.from_template(SYSTEM_SUMMARY_TEMPLATE)
    return RunnablePassthrough() | prompt | llm | StrOutputParser()