# 2. Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.

from pprint import pprint
import requests
import json

main_link = 'https://api.vk.com/method/users.get'

my_params = {'api_id': 7500173,
             'user_ids': 'ivan_lednev',
             'access_token': 'd7f00930eb70594496d02dcc341fa0e945f8229a70fe8890f0cc21e30d827f27129ddcd4584d8c61fb2cc',
             'v': 5.107}

response = requests.get(main_link, params = my_params)
with open('ivan_lednev.json', 'wb') as f:
    f.write(response.content)

pprint(response.json())

