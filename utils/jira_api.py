import os
import json
import requests
from typing import Dict, List
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


def create_task(summary: str, description: str, assigned_id: str, reporter_id: str) -> Dict:    
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


def get_tasks() -> List[Dict]:
    params = {
        'jql': f'project = {os.environ.get("PROJECT_KEY")}',
        'maxResults': 50,
        'startAt': 0,
        'filelds': 'summary, description, assignee, reporter'
    }

    response = requests.request(
        "GET",
        url=f"https://{os.environ.get('DOMAIN')}.atlassian.net/rest/api/2/search",
        params=params,
        headers={"Accept": "application/json"},
        auth=HTTPBasicAuth(os.environ.get('EMAIL'), os.environ.get('JIRA_API_TOKEN'))
    )
    
    if response.status_code != 200:
        print(response.text)
        return [{}]
    
    return [{'name': item['summary'], 'description': item['description'], 'reporter': item['reporter'], 'assigned': item['assignee']} for item in response.json()['issues']]