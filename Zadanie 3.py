from bs4 import BeautifulSoup as bs
import requests
import re
import pandas as pd
from pymongo import MongoClient, database
from pymongo.errors import DuplicateKeyError
from pprint import pprint

vacancy = input('Введите вакансию, которую вы ищете: ')
main_url = 'https://hh.ru/'
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/101.0.4951.67 Safari/537.36'}
params = {'search_field': ['name', 'company_name', 'description'], 'text': f'{vacancy}', 'from': 'suggest_post',
          'clusters': 'true', 'ored_clusters': 'true',
          "enable_snippets": 'true', 'hhtmFrom': 'vacancy_search_list'}

response = requests.get(main_url + '/search/vacancy', params=params, headers=headers)
soup = bs(response.text, 'html.parser')

"""Находим кнопку, переводящую на следующую страницу сайта"""
page = soup.find('div', attrs={'class': 'HH-MainContent HH-Supernova-MainContent'})
page_ch = page.find('a', attrs={'data-qa': 'pager-next'})
page_ch_1 = page_ch.find('span')
page_ch_text = page_ch.attrs['href']

"""В эти списки будем добавлять полученные
данные в виде удобном для  создания датафрейма"""
title = []
min_salary = []
max_salary = []
currency = []


def transformation(string):
    """Функция, которая будет обрабатывать
    текст, полученный из тега"""
    global min_salary, max_salary
    num_list = re.findall("[0-9]+", string)
    if 'от' in string and 'до' in string and int(len(num_list)) == 2:
        min_salary.append(num_list[0])
        max_salary.append(num_list[1])
    elif 'от' in string and int(len(num_list)) == 1:
        min_salary.append(num_list[0])
        max_salary.append('Nan')
    elif 'до' in string and int(len(num_list)) == 1:
        min_salary.append('Nan')
        max_salary.append(num_list[0])
    elif int(len(num_list)) == 2:
        min_salary.append(num_list[0])
        max_salary.append(num_list[1])
    elif int(len(num_list)) == 1:
        min_salary.append(num_list[0])
        max_salary.append(num_list[0])
    elif 'Nan' in string:
        min_salary.append('Nan')
        max_salary.append('Nan')


def currency_split(text):
    """Функция забирает значение валюты"""
    text = text.split()[-1]
    if text[-1] == '.':
        return text[:-1]
    return text


search_vacancy = {'data-qa': 'vacancy-serp__vacancy-title'}
search_salary = {'data-qa': 'vacancy-serp__vacancy-compensation'}
count = 0
id = 0
id_list = []
href_list = []

while True:
    page_ch_text_new = page_ch_text.replace('page=1', f'page={count}')
    response = requests.get(main_url + page_ch_text_new, params=params, headers=headers)
    soup = bs(response.text, 'html.parser')
    for vacancy in list(soup.find_all('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})):
        href_list.append(vacancy.attrs['href'])
        title.append(vacancy.text)
        parent = vacancy.find_parent('div', attrs={'class': ''})
        try:
            search_salary_in_tag = parent.find('span', attrs=search_salary).getText()
            search_salary_in_tag = search_salary_in_tag.replace('\u202f', '')
            currency.append(currency_split(search_salary_in_tag))
            transformation(search_salary_in_tag)
        except AttributeError:
            transformation('Nan' + ' ' + 'Nan')
            currency.append('Nan')
        id_list.append(id)
        id += 1
    count += 1
    if count == 40:
        break

#
# df = pd.DataFrame(
#     {'title': title,
#      'min_salary': min_salary,
#      'max_salary': max_salary,
#      'currency': currency},
#     columns=['title', 'min_salary', 'max_salary', 'currency'])
#
# df.to_csv('vacancy_data_new.csv', sep=' ', index=False)

"""Задание 1"""

"""Сначала пришлось сгенерировать данные для mongo, поскольку я создавал датафрейм  из общих списков"""


def data_values(title_data, min_salary_data, max_salary_data, currency_data, href_data):
    """Функция формирует данные для mongodb"""
    columns_name = ['title', 'min_salary', 'max_salary', 'currency', 'link']
    correct = zip(title_data, min_salary_data, max_salary_data, currency_data, href_data)
    data_element = [dict(zip(columns_name, elements)) for elements in list(correct)]
    return data_element


data = data_values(title, min_salary, max_salary, currency, href_list)


def data_id(database_with_id):
    """Функция создает уникальный id"""
    num = 0
    for el in database_with_id:
        new_el = {'_id': int(el['link'].split('?')[0].split('/')[4])} | el
        database_with_id[num] = new_el
        num += 1
    return database_with_id


full_data = data_id(data)


def mongo(data):
    if type(data) == list:
        return data
    else:
        return list(data)


def add_to_database(databases):
    client = MongoClient('127.0.0.1', 27017)
    db = client['home_work_database_train']
    actual_vacancy = db.actual_vacancy
    mongo_data = mongo(databases)
    for vac in range(len(mongo_data)):
        try:
            actual_vacancy.insert_one(mongo_data[vac])

        except DuplicateKeyError:
            print('please use another id')
            continue
    return actual_vacancy


view_data = add_to_database(full_data)
for i in view_data.find({}):
    print(i)

""" Задание 2"""


def salary_in_vacancy(number: int):
    if type(number) == int:
        for doc in view_data.find({'min_salary': {'$gt': number},
                                   'max_salary': {'$gt': number}}):
            print(doc)
        return ''
    else:
        print('int only')


input_element = int(input('Введите необходимое число: '))
print(f'\n\n\n\n {salary_in_vacancy(input_element)}')
