from langgraph.graph import StateGraph, END
from utils.models import AgentState
import utils.nodes as graph_nodes
from logger import logger

class Agent():
    def __init__(self):
        self.state = self._init_state()
        self.app = self._build_agent()

    def _init_state(self):
        return {
            'input': None,
            'dialog': None,
            'names': None,
            'classify_result': None,
            'users': None,
            'accounts': None,
            'extracted_tasks': None,
            'summary': None,
            'feedback': None,
            'report': None,
            'jira_tasks': None,
            'matched_tasks': None
        }
    
    def _build_agent(self):
        graph = StateGraph(AgentState)

        graph.add_node('tools', graph_nodes.tool_node)
        graph.add_node('classify_query', graph_nodes.classify_query_node)
        graph.add_node('summary', graph_nodes.summary_node)
        graph.add_node('extract_names', graph_nodes.extract_names_node)
        graph.add_node('get_accounts', graph_nodes.get_accounts_node)
        graph.add_node('match_users', graph_nodes.match_users_node)
        graph.add_node('extract_dialog_tasks', graph_nodes.extract_dialog_tasks_node)
        graph.add_node('get_jira_tasks', graph_nodes.get_jira_tasks_node)
        graph.add_node('match_tasks', graph_nodes.match_tasks_node)
        graph.add_node('feedback', graph_nodes.feedback_node)
        graph.add_node('update_tasks', graph_nodes.update_tasks_node)

        graph.set_entry_point('classify_query')
        graph.add_conditional_edges(
            "classify_query",
            lambda state: state['classify_result'],
            {
                "valid dialog": "summary",
                "unvalid dialog": END,
                "query": "feedback",
                "jira": "update_tasks"
            }
        )
        
        graph.add_edge('feedback', END)
        
        graph.add_edge('update_tasks', END)

        graph.add_edge('summary', 'extract_names')
        graph.add_edge('extract_names', 'get_accounts')
        graph.add_edge('get_accounts', 'match_users')
        graph.add_edge('match_users', 'extract_dialog_tasks')
        graph.add_edge('extract_dialog_tasks', 'get_jira_tasks')
        graph.add_edge('get_jira_tasks', 'match_tasks')
        graph.add_edge('match_tasks', END)

        self.graph = graph

        return graph.compile()

    def _print_task(self, task: dict) -> str:
        task_string = f"""- **Задача**: "{task['name']}"\n
    **Описание**: {task['description']}\n
    **Создатель**: {task['reporter']}\n
    **Исполнитель**: {task['assigned']}\n\n"""
        task_string += '---\n'

        return task_string
    
    def _postprocessing(self, state: AgentState):
        if state['classify_result'] == 'not dialog':
            self.state['report'] = state['report']
            return self.state['report']
        
        summary_string = f"""**Краткий пересказ встречи**:\n\n{state['summary']}"""
        tasks_string = "**Результаты встречи**:\n\n"

        tasks_string  += "**Неизменившееся задачи**:\n\n"
        for unchanged_task in state['matched_tasks']['unchanged_tasks']:
            tasks_string += self._print_task(unchanged_task)
        
        tasks_string  += "**Обновленные задачи**:\n\n"
        for updated_task in state['matched_tasks']['updated_tasks']:
            tasks_string += self._print_task(updated_task)
        
        tasks_string  += "**Новые задачи**:\n\n"
        for new_task in state['matched_tasks']['new_tasks']:
            tasks_string += self._print_task(new_task)
        
        report =  '\n\n'.join(["Анализ прошедшей встречи готов.", summary_string, tasks_string])
        self.state['report'] = report
        
        return report
        

    def run(self, user_input: str):
        self.state['input'] = user_input
        logger.info(f'state:\n{self.state}')
        self.state = self.app.invoke(self.state)
        
        return self._postprocessing(self.state)