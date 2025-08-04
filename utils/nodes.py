from utils import jira_api
from typing import TypedDict, Optional, List, Dict
from langgraph.prebuilt import ToolNode
from utils.tools import tools
from utils.llm import get_user_matcher, get_dialog_checker, get_task_extractor, get_summarizer

tool_node = ToolNode(tools=tools) 

class AgentState(TypedDict):
    dialog: Optional[str]
    names: Optional[List[str]]
    is_valid_dialog: bool
    users: Optional[List[Dict[str,str]]]
    accounts: Optional[Dict[str, str]]
    tasks: Optional[Dict[str, str]]
    summary: Optional[str]


def check_dialog_node(state: AgentState) -> AgentState:
    response = get_dialog_checker().invoke({'query': state['dialog']})
    print(f'check dialog responce: {response}')
    
    try:
        state['is_valid_dialog'] = response.result == '1'
    except Exception as e:
        print(f'check dialog error: {e}')
        state['is_valid_dialog'] = False

    return state

def extract_tasks_node(state: AgentState) -> AgentState:
    response = get_task_extractor().invoke({'query': state['dialog']})
    print(f'extract tasks response: {response}')

    try:
        state['tasks'] = response.result
    except Exception as e:
        print('extract tasks error: ', e)
        state['tasks'] = {}
    
    return state


def extract_names_node(state: AgentState) -> AgentState:
    state['names'] = list(set([line.split(':')[0] for line in state['dialog'].split('\n')]))

    return state

def get_accounts_node(state: AgentState) -> AgentState:
    try:
        state['accounts'] = jira_api.get_users()
        print(f'get accounts response: {state["accounts"]}')
    except Exception as e:
        print(f'get account error: {e}')
        state['accounts'] = {}

    return state
    

def match_users_node(state: AgentState) -> AgentState:
    response = get_user_matcher().invoke({'names': state['names'], 'accounts':state['accounts']})
    print(f'match users responce: {response}')
    try:
        state['users'] = response.result
    except Exception as e:
        print(f'match users error: {e}')
        state['users']  = [{'name':'', 'id':''}]

    return state

def summary_node(state: AgentState) -> AgentState:
    response  = get_summarizer().invoke({'query':state['dialog']})
    try:
        state['summary'] = response
    except Exception as e:
        print('summary error: ', e)
        state['summary'] = ''
    
    return state
