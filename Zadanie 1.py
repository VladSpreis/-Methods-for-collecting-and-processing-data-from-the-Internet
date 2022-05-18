import requests
import json


def repo_for_user(name: str):
    url = f'https://api.github.com/users/{name}/repos'
    response = requests.get(url)
    j_data = response.json()
    name_repos = [keys['name'] for keys in j_data]
    return name_repos


repo_for_user_1 = repo_for_user('VladSpreis')
print(repo_for_user_1)

with open('repos_new.json', 'w') as f:
    json.dump(repo_for_user_1, f)
