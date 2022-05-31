from lxml import html
import requests
from pprint import pprint
import re

from nltk.corpus.reader import xpath

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/101.0.4951.67 Safari/537.36'}

"""for mail.ru"""

url_mail = 'https://news.mail.ru/?_ga=2.117169729.671758194.1652629590-1697036102.1648047265'
response_mail = requests.get(url_mail, headers=headers)
dom_mail = html.fromstring(response_mail.text)

xpath_top_mail = "//a[contains(@class,'js-topnews__item')]"
xpath_mail = "//ul[@data-module = 'TrackBlocks']/li"

news_top_mail = dom_mail.xpath(xpath_top_mail)
news_mail = dom_mail.xpath(xpath_mail)

"""for lenta.ru"""

url_lenta = "https://lenta.ru/"
response_lenta = requests.get(url_lenta, headers=headers)
dom_lenta = html.fromstring(response_lenta.text)

xpath_lenta = "//div[contains(@class,'topnews')]/div/a[contains(@class,'card-mini')]"
news_from_lenta = dom_lenta.xpath(xpath_lenta)

"""for yandex"""

url_yandex = "https://yandex.ru/news/"
response_yandex = requests.get(url_yandex, headers=headers)
dom_yandex = html.fromstring(response_yandex.text)

xpath_yandex = "//section[@aria-labelledby='top-heading']/div/div"

news_yandex = dom_yandex.xpath(xpath_yandex)


def check_url(link):
    global url_mail, url_lenta, url_yandex
    if link[0] in url_mail:
        return link[0]
    elif url_yandex in link[0]:
        return link[0]
    else:
        if link[0] in url_lenta:
            return link
        else:
            return url_lenta + link[0]


link_for_yandex = []


def link_page(link):
    """Функция будет создавать запрос на страницу
        где хранится часть необходимой информации"""
    global headers, url_yandex, link_for_yandex
    comp_check = link[0]
    comp_check = comp_check[:23]
    if comp_check == 'https://yandex.ru/news/':
        for_yandex_link = "//article[contains(@class,'news-story')]/h1/a/@href"
        response = requests.get(check_url(link), headers=headers)
        dom = html.fromstring(response.text)
        add_page = dom.xpath(for_yandex_link)  # получение ссылки на последнюю страницу
        link_for_yandex.append(add_page[0])
        response_1 = requests.get(add_page[0], headers=headers)
        dom_1 = html.fromstring(response_1.text)
        return dom_1
    else:
        response = requests.get(check_url(link), headers=headers)
        dom = html.fromstring(response.text)
        return dom


def path_from_yandex_date(response_from_yandex):
    """Функция возвращает необходимы запрос для даты с разных сайтов-источников(необходимо для яндекса"""
    data_list = {'lenta.ru': "//div[contains(@class,'topic-header__left-box')]/time/text()",
                 'www.rbc.ru': "//div[@class='article__header__info-block']/time/@datetime",
                 'ria.ru': "//div[@class='article__info-date']/a/text()",
                 'www.kommersant.ru': "//header/div[@class='doc_header__time']/time/@datetime",
                 'tass.ru': "//dateformat[@class='ng-scope' and @mode='abs']/time/@datetime"}
    split_link = response_from_yandex.split("//")[1].split('/')[0]
    for el in data_list.keys():
        if split_link == el:
            return data_list[el]
        elif split_link is el and el == 'www.kommersant.ru':
            return data_list[el][0]


def if_not_data(variable):
    if not variable:
        return 'No data'
    else:
        return variable[0]


list_news_from_mail = []
list_news_from_lenta = []
list_news_yandex = []


def source_for_yandex(link):
    split_link = link[0][8:].split('/'[0])
    return split_link


def add_data(xpath_1, title_1, link_1, source_1, date):
    global list_news_from_mail, list_news_from_lenta, list_news_yandex
    dict_for_news = {}
    prep_title_news = if_not_data(title_1)
    title_for_news_main = prep_title_news.replace('\xa0', ' ')
    new_source_for_news = if_not_data(source_1)
    datetime = if_not_data(date)
    link_main = if_not_data(link_1)
    dict_for_news['title'] = title_for_news_main
    dict_for_news['source'] = new_source_for_news
    dict_for_news['link'] = link_main
    dict_for_news['datetime'] = datetime
    if xpath_1 == xpath_top_mail or xpath_1 == xpath_mail:
        list_news_from_mail.append(dict_for_news)
    elif xpath_1 is xpath_lenta:
        list_news_from_lenta.append(dict_for_news)


def parcing(news_tag, xpath, title='', link='', source='', date=''):
    global list_news_from_mail, list_news_from_lenta, xpath_mail, xpath_top_mail, xpath_lenta, url_lenta, url_yandex, link_for_yandex
    for news in news_tag:
        title_news = news.xpath(title)
        link_for_news = news.xpath(link)
        if xpath == xpath_mail or xpath == xpath_top_mail or xpath == xpath_lenta:
            source_for_news = link_page(link_for_news).xpath(source)
            datetime_for_news = link_page(link_for_news).xpath(date)
            add_data(xpath, title_news, link_for_news, source_for_news, datetime_for_news)
        elif xpath == xpath_yandex:
            datetime_for_news = link_page(link_for_news).xpath(path_from_yandex_date(link_for_yandex[0]))
            prep_source = news.xpath(source)  # яндекс выдает название  другого информационного сайт как источника
            add_data(xpath, title_news, link_for_news, prep_source, datetime_for_news)


parcing(news_top_mail[:-2], xpath_top_mail,
        title="./span/span[not(contains(@class,'photo__subtitle'))]/text()",
        link="./@href",
        source=".//span[@class='note']//span[@class='link__text']/text()",
        date=".//span[contains(@class,'note__text')]/@datetime")

parcing(news_mail, xpath_mail, title=".//a[@class='list__text']//text()",
        link=".//a[@class='list__text']/@href",
        source=".//span[@class='note']/a//text()",
        date=".//span[contains(@class,'note__text')]/@datetime")

pprint(list_news_from_mail)

parcing(news_from_lenta, xpath_lenta, title=".//span/text()",
        link="./@href",
        source=".//a[contains(@class,'topic-header__item')]/text()",
        date=".//time[contains(@class,'topic-header__item')]/text()")

pprint(list_news_from_lenta)

parcing(news_yandex, xpath_yandex, title=".//h2/a/text()", link=".//h2/a/@href",
        source=".//span[contains(@class,'mg-card-source__source')]/a/text()",
        date="")

pprint(list_news_yandex)
