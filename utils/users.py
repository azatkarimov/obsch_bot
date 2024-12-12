import json

USERS_PATH = 'data/users.json'
with open(USERS_PATH, 'r', encoding='utf-8') as users:
    users_data = json.load(users)


def update_users_data(data):
    with open(USERS_PATH, 'w', encoding='utf-8') as write_users:
        json_data = json.dumps(data, indent=4)
        write_users.write(json_data)
