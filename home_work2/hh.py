from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import pandas as pd
import re
import json

def split_salary(text):
    """
    функция для обработки зарплаты
    """
    global max_salary
    global min_salary
    global currency
    text = salary_tag.text.replace(u'\xa0', u'')
    # print(text)
    if re.search(r'-', text):
        min_salary = int(re.findall(r'^\d+', text)[0])
        max_salary = int(re.findall(r'-(\d+)', text)[0])
        currency = re.findall(r'\s(.+)', text)[0]
        # print(min_salary)
        # print(max_salary)
        # print(currency)
    elif re.search(r'от', text):
        min_salary = int(re.findall(r'\s(\d+)', text)[0])
        currency = re.findall(r'\s\d+\s(.+)', text)[0]
        # print(min_salary)
        # print(currency)
    elif re.search(r'до', text):
        max_salary = int(re.findall(r'\s(\d+)', text)[0])
        currency = re.findall(r'\s\d+\s(.+)', text)[0]
        # print(max_salary)
        # print(currency)


main_link = 'https://www.hh.ru'
prof = input('Enter profession: ')
params_hh = {'text': prof,
             'area': 2}  # petersburg
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}

response = requests.get(main_link + '/search/vacancy', headers=headers, params=params_hh)
vacancies = []

# with open('hh.html', 'r', encoding='utf-8') as f:
#     soup = bs(f.read(), 'html.parser')

# with open('sj.html', 'w', encoding='utf-8') as f:
#     f.write(response.text)

"""
main_link2 = 'https://russia.superjob.ru'
params_sj = {'keywords': prof}
             #'geo%5Bc%5D%5B0%5D': 4}  # москва

response = requests.get(main_link2 + '/vacancy/search/', params=params_sj)


soup = bs(response.text, 'html.parser')
vacancy_block = soup.find('div', {'style': 'display:block'})
vacancy_list = vacancy_block.findChildren(recursive=False)
print(len(vacancy_list))
"""

while True:
    soup = bs(response.text, 'html.parser')

    vacancy_block = soup.find('div', {'class': 'vacancy-serp'})
    vacancy_list = vacancy_block.findChildren('div', attrs={'class':'vacancy-serp-item'}) #findChildren(recursive=False)
    child = vacancy_block.findChild()
    for vacancy in vacancy_list:  # vacancy_list:
        vacancies_data = {}
        # проверяем не реклама ли
        # if vacancy['class'].count('serp-special') == 0:
        tag = vacancy.find('a', {'data-qa':'vacancy-serp__vacancy-title'})
        link = re.split(r'\?', tag['href'])[0]
        name = tag.text
        max_salary = None
        min_salary = None
        currency = None
        salary_tag = vacancy.find('div', {'class':'vacancy-serp-item__sidebar'}).findChild()
        if salary_tag:
            split_salary(salary_tag.text)

        vacancies_data['Name'] = name
        vacancies_data['Link'] = link
        vacancies_data['Min salary'] = min_salary
        vacancies_data['Max salary'] = max_salary
        vacancies_data['Currency'] = currency
        vacancies_data['Source link'] = main_link

        vacancies.append(vacancies_data)

    page_next = soup.find('a', {'data-qa':'pager-next'})
    if page_next:
        link_page_next = page_next['href']
        response = requests.get(main_link + link_page_next, headers=headers)
    else:
        break


df = pd.DataFrame(vacancies, columns=['Name', 'Link', 'Min salary', 'Max salary', 'Currency', 'Source link'])
pprint(df)

# with open(prof + '.json', 'w', encoding='utf-8') as f:
#     json.dump(vacancies, f)

# df.to_csv('df.csv', encoding='utf-8')
