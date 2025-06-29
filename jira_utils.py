import os
import requests
import json
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

auth = HTTPBasicAuth(os.environ.get('EMAIL'), os.environ.get('JIRA_API_TOKEN'))
domain = os.environ.get('DOMAIN')

def get_project(key:str):
    response = requests.request(
        "GET",
        url=f"https://{domain}.atlassian.net/rest/api/2/project/{key}",
        headers={"Accept": "application/json"},
        auth=auth
    )

    if response.status_code != 200:
        print(response.text)
        return {}

    return response.json()

def get_users():
    response = requests.request(
        "GET",
        url=f"https://{domain}.atlassian.net/rest/api/2/users/search",
        headers={"Accept": "application/json"},
        auth=auth
    )

    if response.status_code != 200:
        return []

    return [user for user in response.json() if user['accountType'] == 'atlassian']

def create_task(summary: str, description: str, assigned_id: str, reporter_id: str):    
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
        url=f"https://{domain}.atlassian.net/rest/api/2/issue",
        data=payloads,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        auth=auth
    )

    if response.status_code != 200:
        print(response.text)
        return {}
    
    return response.json()

users = get_users()
for user in users:
    print(user['accountId'], user['displayName'])

task_params = {
    'summary':'test request summar2y',
    'description': 'test requesdt descr',
    'assigned_id':'62010cc3ff9289006eeaf4c6',
    'reporter_id': '62010cc3ff9289006eeaf4c6',
}

print(create_task(**task_params))
