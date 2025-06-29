import os
from pydantic import SecretStr
from omegaconf import DictConfig
from langchain_openai import ChatOpenAI
from utils.templates import SYSTEM_TASK_TEMPLATE
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.utils.json import parse_json_markdown

class LLMOpenRouter(ChatOpenAI):
        def __init__(self, config: DictConfig):
            super().__init__(base_url="https://openrouter.ai/api/v1", 
                            api_key=SecretStr(os.environ.get("OPENROUTER_API_KEY") or ""),
                            model=config.llm.model_name,
                            temperature=config.llm.temperature,
                            top_p=config.llm.top_p,
                            presence_penalty=config.llm.repeat_penalty)

class LLMWorker():
    def __init__(self, config: DictConfig):
        self.llm = LLMOpenRouter(config)
        self.history = []
    
    def _run_llm(self, system_prompt: str, **input_params):
        prompt = ChatPromptTemplate([
            ('system', system_prompt),
            MessagesPlaceholder('history', optional=True),
            ('human', '{query}')
        ])
        chain = prompt | self.llm | StrOutputParser()

        return chain.invoke(input_params)
    
    def extract_tasks(self, query: str):
        llm_output = self._run_llm(SYSTEM_TASK_TEMPLATE, **{'query':query})
        
        try:
             structed_output = parse_json_markdown(llm_output)
        except:
             print(llm_output)
             structed_output = [{'name':'', 'task':''}]
             
        return structed_output