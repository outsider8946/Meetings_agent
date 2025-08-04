from langgraph.graph import StateGraph, END
from utils.nodes import (check_dialog_node, extract_names_node, extract_tasks_node, summary_node,
                         get_accounts_node, match_users_node, tool_node, AgentState)

class Agent():
    def __init__(self):
        self.app = self._build_agent()

    def _build_agent(self):
        graph = StateGraph(AgentState)

        graph.add_node('tools', tool_node)
        graph.add_node('check_dialog', check_dialog_node)
        graph.add_node('summary', summary_node)
        graph.add_node('extract_names', extract_names_node)
        graph.add_node('get_accounts', get_accounts_node)
        graph.add_node('match_users', match_users_node)
        graph.add_node('extract_tasks', extract_tasks_node)

        graph.set_entry_point('check_dialog')
        graph.add_conditional_edges(
            "check_dialog",
            lambda state: "valid_dialog" if state['is_valid_dialog'] else "unvalid_dialog",
            {
                "valid_dialog": "summary",
                "unvalid_dialog": END
            }
        )
        graph.add_edge('summary', 'extract_names')
        graph.add_edge('extract_names', 'get_accounts')
        graph.add_edge('get_accounts', 'match_users')
        graph.add_edge('match_users', 'extract_tasks')
        graph.set_finish_point('extract_tasks')

        self.graph = graph

        return graph.compile()
    
    
    def _postprocessing(self, state: AgentState):
        summary_string = f"""**Краткий пересказ встречи**:\n\n{state['summary']}"""
        tasks_string = "**Результаты встречи**:\n\n"

        for item in state['tasks']:
            tasks_string += f"""- **Задача**: "{item['name']}"\n
    **Описание**: {item['description']}\n
    **Создатель**: {item['owner']}\n
    **Исполнитель**: {item['reported by']}\n\n"""
            tasks_string += '---\n'
        
        return '\n\n'.join(["Анализ прошедшей встречи готов.", summary_string, tasks_string])
        

    def start(self, dialog):
        state = AgentState(**{
            'dialog':dialog,
            'names': None,
            'is_valid_dialog': False,
            'is_valid_names': False,
            'template': None,
            'users': None,
            'message': None,
            'accounts': None,
            'summary': None
        })
 
        return self._postprocessing(self.app.invoke(state))

    def debug(self, dialog):
        state = AgentState(**{
            'dialog':dialog,
            'names': None,
            'is_valid_dialog': False,
            'is_valid_names': False,
            'template': None,
            'users': None,
            'message': None,
            'accounts': None,
            'tasks': None,
            'summary': None
        })

        return [step for step in self.app.stream(input=state, stream_mode='debug')]