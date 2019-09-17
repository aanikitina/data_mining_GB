import requests
import json

#  constants
LOGIN = ''  # GitHub login
PASSW = ''  # GitHub password

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15'


def get_git_repos(user_name, auth=False, suffix='', **kwargs):
    git_hub_api = 'https://api.github.com/users'

    if auth:
        login = kwargs['login']
        passw = kwargs['passw']
        auth_arg = requests.auth.HTTPBasicAuth(login, passw)
        suffix += '_auth'
    else:
        auth_arg = None

    response = requests.get(f'{git_hub_api}/{user_name}/repos', headers={'User-Agent': USER_AGENT}, auth=auth_arg)

    print(f'STATUS: {response.status_code}')

    if auth:
        print(f'AUTHORIZATION: {response.request.headers["Authorization"].split()[0]}')

    if response.status_code < 400:
        with open(f'{user_name}_repos{suffix}.json', 'w') as out_f:

            for item in response.json():
                print(f'{item["id"]}, {item["name"]}')

            json.dump(response.json(), out_f, ensure_ascii=False, indent=4)
    else:
        print('Invalid status')


get_git_repos(LOGIN)  # Task 1: print repos
get_git_repos(LOGIN, auth=True, login=LOGIN, passw=PASSW)  # Task 2: use authorization

# print(1)
