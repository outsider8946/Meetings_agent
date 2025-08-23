from logger import logger
from utils.config_loader import config
from utils import jira_api
from langgraph.prebuilt import ToolNode
from utils.tools import tools
from utils.llm import LLMWorker
from utils.templates import SYSTEM_DIALOG_VALIDATE, SYSTEM_MATCH_USERS, SYSTEM_TASK_TEMPLATE, SYSTEM_SUMMARY_TEMPLATE, SYSTEM_FEEDBACK
from utils.models import AgentState, DialogValidator, TaskValidator, UserValidator

tool_node = ToolNode(tools=tools) 
_llm = LLMWorker(config)


def dialog_validate_node(state: AgentState) -> AgentState:
    logger.info(f'state in node:\n{state}')
    response = _llm(input={'query': state['input']}, template=SYSTEM_DIALOG_VALIDATE, validator=DialogValidator)
    logger.info(f'dialog validate result: {response}')
    state['validate_result'] = response

    if state['validate_result'] == 'not dialog':
        state['feedback'] = state['input']
    else:
        state['dialog'] = state['input']

    return state


def extract_tasks_node(state: AgentState) -> AgentState:
    response = _llm(input={'query':state['dialog']}, template=SYSTEM_TASK_TEMPLATE, validator=TaskValidator)
    logger.info(f'extracted tasks: {response}')
    state['tasks'] = response
    
    return state


def create_tasks_node(state: AgentState) -> AgentState:
    def get_id_by_name(name: str) -> str:
        if state['users'] is None:
            return ''
        
        for item in state['users']:
            if item['name'] == name:
                return item['id']
        return ''

    if state['tasks'] is None:
        return state
    
    for task in state['tasks']:
        assigned_id = get_id_by_name(task['assigned'])
        reporter_id = get_id_by_name(task['reporter'])

        try:
            jira_api.create_task(summary=task['name'], description=task['description'],
                                assigned_id=assigned_id, reporter_id=reporter_id)
        except Exception as e:
            logger.error(f'Task {task["name"]} not done with error {e}')
    
    return state


def extract_names_node(state: AgentState) -> AgentState:
    state['names'] = list(set([line.split(':')[0] for line in state['dialog'].split('\n')]))
    logger.info(f'extracted names: {state["names"]}')

    return state


def get_accounts_node(state: AgentState) -> AgentState:
    try:
        state['accounts'] = jira_api.get_users()
        logger.info(f'accounts: {state["accounts"]}')
    except Exception as e:
        logger.error(f'get account error: {e}')
        state['accounts'] = {}

    return state
    

def match_users_node(state: AgentState) -> AgentState:
    response = _llm(input={'names': state['names'], 'accounts':state['accounts']}, template=SYSTEM_MATCH_USERS, validator=UserValidator)
    logger.info(f'match users result: {response}')
    state['users'] = response

    return state


def summary_node(state: AgentState) -> AgentState:
    response = _llm(input={'query':state['dialog']}, template=SYSTEM_SUMMARY_TEMPLATE, validator=None)
    state['summary'] = response
    logger.info('summary is done')
    
    return state


def feedback_node(state: AgentState) -> AgentState:
    response = _llm(input={'dialog':state['dialog'], 'report':state['report'], 'feedback':state['feedback']}, template=SYSTEM_FEEDBACK, validator=None)
    state['report'] = response
    logger.info('applying feedback is done')

    return state

def get_tasks_node(state :AgentState) -> AgentState:
    tasks = jira_api.get_tasks()
    return state