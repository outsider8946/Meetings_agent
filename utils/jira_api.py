import os
import json
import requests
from typing import Dict, List, Optional
from requests.auth import HTTPBasicAuth

def get_users() -> Dict:
    response = requests.request(
        "GET",
        url=f"https://{os.environ.get('DOMAIN')}.atlassian.net/rest/api/2/users/search",
        headers={"Accept": "application/json"},
        auth=HTTPBasicAuth(os.environ.get('EMAIL'), os.environ.get('JIRA_API_TOKEN'))
    )

    if response.status_code != 200:
        return {'error':response.json()}
    
    return {user['displayName']:user['accountId'] for user in response.json() if user['accountType'] == 'atlassian'}


def get_user_id_by_name(name: str) -> str:
        users_dict = get_users()
        if 'error' in users_dict.keys():
            return ''
        else:
            users = list(users_dict.keys())
        
        for item in users:
            if item['name'] == name:
                return item['id']
        return ''


def create_task(users: Optional[List], summary: str, description: str, assigned: str, reporter: str) -> Dict:
    assigned_id = get_user_id_by_name(assigned)
    reporter_id = get_user_id_by_name(reporter)    
    payloads = json.dumps({
        "fields": {
            "assignee": {"id": assigned_id},
            "description": description,
            "project":{"key":os.environ.get('PROJECT_KEY')},
            "reporter": {"id":reporter_id},
            "summary":summary,
            "issuetype":{'name':'Task'},    
        }
    })

    response = requests.request(
        'POST',
        url=f"https://{os.environ.get('DOMAIN')}.atlassian.net/rest/api/2/issue",
        data=payloads,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        auth=HTTPBasicAuth(os.environ.get('EMAIL'), os.environ.get('JIRA_API_TOKEN'))
    )

    if response.status_code != 200:
        print(response.text)
        return {}
    
    return response.json()


def update_task(task_id: str, description: str) -> Dict:
    data = json.dumps({
        "update":{
            "description": [
                {
                    "set": description
                }
            ]
        }
    })

    response = requests.request(
        "PUT",
        url=f"https://{os.environ.get('DOMAIN')}.atlassian.net/rest/api/2/issue/{task_id}",
        data=data,
        headers={"Accept": "application/json"},
        auth=HTTPBasicAuth(os.environ.get('EMAIL'), os.environ.get('JIRA_API_TOKEN'))
    )

    if response.status_code != 200:
        print(response.text)
        return {}
    
    return response.json()


def get_tasks() -> List[Dict]:
    params = {
        'jql': f'project = {os.environ.get("PROJECT_KEY")}',
        'maxResults': 50,
        'startAt': 0,
        'fields': 'id, summary, description, assignee, reporter'
    }

    response = requests.request(
        "GET",
        url=f"https://{os.environ.get('DOMAIN')}.atlassian.net/rest/api/3/search/jql",
        params=params,
        headers={"Accept": "application/json"},
        auth=HTTPBasicAuth(os.environ.get('EMAIL'), os.environ.get('JIRA_API_TOKEN'))
    )
    
    if response.status_code != 200:
        print(response.text)
        return [{}]

    result = []
    for item in response.json()['issues']:
        result.append({
            'name': item['fields']['summary'],
            'description': item['fields']['description'],
            'reporter': item['fields']['reporter']['displayName'],
            'assigned': item['fields']['assignee']['displayName']
        })

    
    return result


update_task(task_id='', description='Олег продолжает изучать аналогичные решения')