from pymongo import MongoClient
from pprint import pprint
import json

def find_vacancies():
    try:
        num = int(input('Enter the required salary: '))
    except ValueError:
        print('Not an integer.')
        return
    for vacan in vacancies.find({'$or': [{'Max salary': {'$gte': num}}, {
        '$and': [{'Min salary': {'$nin': [None]}}, {'Max salary': {'$in': [None]}}]}]}):
        pprint(vacan)

def insert_data(db, vacancies):
    ''' Добавление неповторяющихся вакансий в БД
     (критерий повторения ссылка, в которой содержится id вакнсии)
     с помощью метода upsert'''
    for pos in vacancies:
        new_link = pos['Link']
        db.update_one({'Link': new_link}, {'$set': pos}, upsert=True)


with open('big data.json', 'r', encoding='utf-8') as f:
    vacancy_list = json.load(f)

client = MongoClient('localhost', 27017)
db = client['hh_db']
vacancies = db.vacancies

insert_data(vacancies, vacancy_list)
find_vacancies()





