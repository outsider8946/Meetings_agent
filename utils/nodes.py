from logger import logger
from utils.config_loader import config
from utils import jira_api
from langgraph.prebuilt import ToolNode
from utils.tools import tools
from utils.llm import LLMWorker
from utils.templates import *
from utils.models import AgentState, ClassifyValidator, TaskValidator, UserValidator, MatchTaskValidator

tool_node = ToolNode(tools=tools) 
_llm = LLMWorker(config)


def classify_query_node(state: AgentState) -> AgentState:
    """Node to classify user query"""

    logger.info(f'state in node:\n{state}')
    response = _llm(input={'query': state['input']}, 
                    template=SYSTEM_INPUT_VALIDATE_TEMPLATE, 
                    validator=ClassifyValidator)
    logger.info(f'dialog validate result: {response}')
    state['classify_result'] = response

    if state['classify_result'] == 'not dialog':
        state['feedback'] = state['input']
    else:
        state['dialog'] = state['input']

    return state


def extract_dialog_tasks_node(state: AgentState) -> AgentState:
    """Node to extract tasks from user dialog"""

    response = _llm(input={'query':state['dialog']}, 
                    template=SYSTEM_TASK_TEMPLATE, 
                    validator=TaskValidator)
    logger.info(f'extracted tasks: {response}')
    state['extracted_tasks'] = response
    
    return state


def extract_names_node(state: AgentState) -> AgentState:
    """Node to extract names of dialog participiants from user dialog"""

    state['names'] = list(set([line.split(':')[0] for line in state['dialog'].split('\n')]))
    logger.info(f'extracted names: {state["names"]}')

    return state


def get_accounts_node(state: AgentState) -> AgentState:
    """Node to get jira accounts"""

    try:
        state['accounts'] = jira_api.get_users()
        logger.info(f'accounts: {state["accounts"]}')
    except Exception as e:
        logger.error(f'get account error: {e}')
        state['accounts'] = {}

    return state
    

def match_users_node(state: AgentState) -> AgentState:
    """Node to find real users for current jira project"""

    response = _llm(input={'names': state['names'], 
                           'accounts':state['accounts']},
                            template=SYSTEM_MATCH_USERS_TEMPLATE, 
                            validator=UserValidator)
    logger.info(f'match users result: {response}')
    state['users'] = response

    return state


def summary_node(state: AgentState) -> AgentState:
    """Node to summary user dialog"""

    response = _llm(input={'query':state['dialog']}, 
                    template=SYSTEM_SUMMARY_TEMPLATE, 
                    validator=None)
    state['summary'] = response
    logger.info('summary is done')
    
    return state


def feedback_node(state: AgentState) -> AgentState:
    """Node to change report by user feedback"""

    response = _llm(input={'dialog':state['dialog'], 
                           'report':state['report'], 
                           'feedback':state['feedback']},
                           template=SYSTEM_FEEDBACK_TEMPLATE, 
                           validator=None)
    state['report'] = response
    logger.info('applying feedback is done')

    return state

def get_jira_tasks_node(state: AgentState) -> AgentState:
    """Node to get jira tasks for current project"""

    tasks = jira_api.get_tasks()

    for i, task in enumerate(tasks):
        logger.info(f'Jira tasks №{i}:\n {task}')

    state['jira_tasks'] = tasks

    return state


def match_tasks_node(state: AgentState) -> AgentState:
   """Node to match new/updated jira tasks with dialog user"""

   response = _llm(input={'jira_tasks': state['jira_tasks'],
                          'extracted_tasks': state['extracted_tasks']},
                          template=SYSTEM_MATCH_TASKS_TEMPLATE, 
                          validator=MatchTaskValidator)
   state['matched_tasks'] = response

   return state


def update_tasks_node(state: AgentState) -> AgentState:
    """Node to create/update jira tasks"""

    if state['matched_tasks'] is None:
        return state
    
    for updated_task in state['matched_tasks']['updated_tasks']:
        try:
            jira_api.update_task(
                task_id=updated_task['id'], 
                description=updated_task['description']
            )
        except Exception as e:
            logger.error(f"Error to update task {updated_task['id']} -- {updated_task['name']}:\n{e}")
    
    for new_task in state['matched_tasks']['new_tasks']:
        try:
            jira_api.create_task(
                summary=new_task['name'],
                description=new_task['description'],
                assigned=new_task['assigned'],
                reporter=new_task['reporter']
            )
        except Exception as e:
            logger.error(f"Error to create new task {new_task['id']} -- {new_task['name']}:\n{e}")
    
    return state