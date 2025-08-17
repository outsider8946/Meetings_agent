from langgraph.graph import StateGraph, END
import utils.nodes as graph_nodes

class Agent():
    def __init__(self):
        self.state =  self._init_state()
        self.app = self._build_agent()
    
    def _init_state(self):
        return graph_nodes.AgentState(**{
            'input': None,
            'dialog':None,
            'names': None,
            'validate_result': False,
            'users': None,
            'accounts': None,
            'tasks': None,
            'summary': None,
            'feedback': None,
            'report': None
        })

    def _build_agent(self):
        graph = StateGraph(graph_nodes.AgentState)

        graph.add_node('tools', graph_nodes.tool_node)
        graph.add_node('dialog_validate', graph_nodes.dialog_validate_node)
        graph.add_node('summary', graph_nodes.summary_node)
        graph.add_node('extract_names', graph_nodes.extract_names_node)
        graph.add_node('get_accounts', graph_nodes.get_accounts_node)
        graph.add_node('match_users', graph_nodes.match_users_node)
        graph.add_node('extract_tasks', graph_nodes.extract_tasks_node)
        graph.add_node('feedback', graph_nodes.feedback_node)

        graph.set_entry_point('dialog_validate')
        graph.add_conditional_edges(
            "dialog_validate",
            lambda state: state['validate_result'],
            {
                "valid dialog": "summary",
                "unvalid dialog": END,
                "not dialog": "feedback"
            }
        )
        
        graph.add_edge('feedback', END)

        graph.add_edge('summary', 'extract_names')
        graph.add_edge('extract_names', 'get_accounts')
        graph.add_edge('get_accounts', 'match_users')
        graph.add_edge('match_users', 'extract_tasks')
        graph.add_edge('extract_tasks', END)

        self.graph = graph

        return graph.compile()
    
    
    def _postprocessing(self, state: graph_nodes.AgentState):
        if state['validate_result'] == 'not dialog':
            self.state['report'] = state['report']
            return self.state['report']
        
        summary_string = f"""**Краткий пересказ встречи**:\n\n{state['summary']}"""
        tasks_string = "**Результаты встречи**:\n\n"

        for item in state['tasks']:
            tasks_string += f"""- **Задача**: "{item['name']}"\n
    **Описание**: {item['description']}\n
    **Создатель**: {item['owner']}\n
    **Исполнитель**: {item['reported by']}\n\n"""
            tasks_string += '---\n'
        
        report =  '\n\n'.join(["Анализ прошедшей встречи готов.", summary_string, tasks_string])
        self.state['report'] = report
        
        return report
        

    def run(self, user_input: str):
        self.state['input'] = user_input
        self.state = self.app.invoke(self.state)
        
        return self._postprocessing(self.state)