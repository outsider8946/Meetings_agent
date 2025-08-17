import os
from dotenv import load_dotenv
from omegaconf import DictConfig
from typing import Dict, Optional, Type, TypeVar
from pydantic import SecretStr
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from langchain_core.runnables import RunnablePassthrough


T = TypeVar('T', bound=BaseModel)

class LLMWorker():
    def __init__(self, config: DictConfig):
        load_dotenv()
        self.llm = ChatOpenAI(base_url="https://openrouter.ai/api/v1", 
                                api_key=SecretStr(os.environ.get("OPENROUTER_API_KEY") or ""),
                                model=config.llm.model_name,
                                temperature=config.llm.temperature,
                                top_p=config.llm.top_p,
                                default_headers={
                                    "HTTP-Referer": "http://localhost:8501",
                                    "X-Title": "Meetings Agent"
                                }
                    )
    
    def __call__(self, input: Dict[str, str], template: str, validator: Optional[Type[T]] = None):
        prompt = ChatPromptTemplate.from_template(template)
        
        if validator:
            llm = self.llm.with_structured_output(validator)
        else:
            llm = self.llm
            
        chain = RunnablePassthrough() | prompt | llm
        out = chain.invoke(input)
        
        if validator:
            out = out.result
        else:
            out = out.content
    
        return out 