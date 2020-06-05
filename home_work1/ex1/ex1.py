# 1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев
# для конкретного пользователя, сохранить JSON-вывод в файле *.json.
from pprint import pprint
import requests
import json

main_link = 'https://api.github.com/users/komarovko90/repos'
headers = {'Accept': 'application/vnd.github.v3+json'}

response = requests.get(main_link, headers=headers)
with open('komarovko90.json', 'wb') as f:
    f.write(response.content)

param = response.json()

# with open('komarovko90.json', 'r') as f:
#     param = json.load(f)

for repo in param:
    print(repo['html_url'])


