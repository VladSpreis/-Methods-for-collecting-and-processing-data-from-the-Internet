from bs4 import BeautifulSoup as bs
import requests
import re
import pandas as pd

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

while True:
    page_ch_text = page_ch_text.replace('page=1', f'page={count}')
    response = requests.get(main_url + page_ch_text, params=params, headers=headers)
    soup = bs(response.text, 'html.parser')
    for vacancy in list(soup.find_all('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})):
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

df = pd.DataFrame(
    {'title': title,
     'min_salary': min_salary,
     'max_salary': max_salary,
     'currency': currency},
    columns=['title', 'min_salary', 'max_salary', 'currency'])

df.to_csv('vacancy_data_new.csv', sep=' ', index=False)
print(df)
