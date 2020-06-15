from lxml import html
import requests
from pprint import pprint
import re
from datetime import datetime, timedelta
from pymongo import MongoClient


def split_date_source_ya (text):
    """
    функция для разделения строки на дату и источник на яндекс.ру
    """
    d = text.split(' ')[-1:]
    source = ' '.join(text.split(' ')[:-1])
    d = re.sub(r'\&nbsp;', ' ', d[0])
    h = int(re.findall(r'(\d+):', d)[0])
    m = int(re.findall(r':(\d+)', d)[0])
    if re.search(r'вчера', d):
        now = datetime.now()
        news_date = datetime(now.year, now.month, now.day, h, m) - timedelta(days=1)
    elif re.search(r'[яфмлйнтод]', d):
        day = int(re.findall(r'\d+', d)[0])
        # num_month = {'января': 1 ,'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6,
        #          'июля': 7, 'августа': 8, 'сентября': 9, 'октября': 10, 'ноября': 11,
        #          'декабря': 12}
        month = re.findall(r'\s(\w+)', d)[0]
        now = datetime.now()
        news_date = datetime(now.year, num_month[month], day, h, m)
    else:
        now = datetime.now()
        news_date = datetime(now.year, now.month, now.day, h, m) - timedelta(days=1)
    return source, news_date

def parsing_ya():
    '''Парсинг yandex.ru'''
    link_ya = 'https://yandex.ru'
    response_ya = requests.get(link_ya + '/news', headers=header)
    dom_ya = html.fromstring(response_ya.text)

    block_news = dom_ya.xpath("//div[@aria-labelledby='computers']//td[@class='stories-set__item']")

    for block in block_news:
        item = {}
        str_time = block.xpath(".//div[@class='story__date']/text()")[0]
        source, date = split_date_source_ya(str_time)
        link = link_ya + block.xpath(".//a[contains(@class, 'link_theme_black')]/@href")[0]
        name = block.xpath(".//a[contains(@class, 'link_theme_black')]/text()")[0]

        item['name'] = name
        item['link'] = link
        item['news date'] = date.strftime("%d.%m.%Y %H:%M")
        item['news source'] = source
        news.append(item)


def parsing_lenta():
    '''Парсинг lenta.ru'''
    link_lenta = 'https://lenta.ru'
    response_lenta = requests.get(link_lenta, headers=header)
    dom_lenta = html.fromstring(response_lenta.text)
    block_news = dom_lenta.xpath("//section[contains(@class,'top7')]/div/div[contains(@class,'item')]")
    source = "Lenta.ru"
    for block in block_news:
        item = {}
        t = block.xpath(".//time/@datetime")[0]
        month = re.findall(r'[А-Яа-я]+', t)[0]
        date = re.sub(month, str(num_month[month]), t)
        date = datetime.strptime(date, ' %H:%M, %d %m %Y')
        link = link_lenta + block.xpath(".//a[contains(@href,'/news')]/@href")[0]
        name = block.xpath(".//a[contains(@href,'/news')]/text()")[0]

        item['name'] = name
        item['link'] = link
        item['news date'] = date.strftime("%d.%m.%Y %H:%M")
        item['news source'] = source
        news.append(item)

def parsing_mail():
    '''Парсинг мэйл.ru'''
    link_mail = 'https://news.mail.ru'
    response_mail = requests.get(link_mail, headers=header)
    dom_mail = html.fromstring(response_mail.text)
    block_news = dom_mail.xpath("//div[@class='daynews__item daynews__item_big'] | //div[@class='daynews__item']")
    for block in block_news:
        item = {}
        link = link_mail + block.xpath("./a/@href")[0]
        name = block.xpath(".//span[contains(@class, 'photo__title')]/text()")[0]

        second_resp = requests.get(link, headers=header)
        second_dom = html.fromstring(second_resp.text)
        second_block = second_dom.xpath("//div[contains(@class, 'breadcrumbs_article')]")
        str_t = second_block[0].xpath(".//span[contains(@class, 'js-ago')]/@datetime")[0]
        date = re.sub('T', ' ', re.split(r'\+', str_t)[0])
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        source = second_block[0].xpath(".//span[@class='link__text']/text()")[0]

        item['name'] = name
        item['link'] = link
        item['news date'] = date.strftime("%d.%m.%Y %H:%M")
        item['news source'] = source
        news.append(item)


num_month = {'января': 1 ,'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6,
             'июля': 7, 'августа': 8, 'сентября': 9, 'октября': 10, 'ноября': 11,
             'декабря': 12}

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}
news = []

parsing_ya()
parsing_lenta()
parsing_mail()


# pprint(news)
client = MongoClient('localhost', 27017)
db = client['hh_db']
db_news = db.news
# db_news.delete_many({})

for pos in news:
    new_name = pos['name']
    pos['update_at'] = datetime.now().strftime("%d.%m.%Y %H:%M")
    db_news.update_one({'name': new_name}, {'$set': pos}, upsert=True)

for pos in db_news.find({}):
    pprint(pos)