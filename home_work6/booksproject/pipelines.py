# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import re
from pymongo import MongoClient
from datetime import datetime


class BooksprojectPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['hh_db']

    def process_item(self, item, spider):
        if spider.name == 'labirint':
            new_item = {'book_id': int(re.findall(r'\d+', item['book_id'])[0]),
                        'book_name':  item['book_name'],
                        'book_link': item['book_link'],
                        'book_authors': item['book_authors'],
                        'book_price': int(item['book_price']),
                        'book_price_sale': int(item['book_price_sale']),
                        'book_rating': float(item['book_rating']),
                        'update_at': datetime.now().strftime("%d.%m.%Y %H:%M")}
            collection = self.db[spider.name]
            book_id = new_item['book_id']
            collection.update_one({'book_id': book_id}, {'$set': new_item}, upsert=True)
        elif spider.name == 'book24':
            # не нулевое ли значение price
            if item['book_price']:
                price = re.sub(r' ', r'', item['book_price'])
                price = int(re.findall(r'\d+', price)[0])
            else:
                price = None
            # не нулевое ли значение price_sale
            if item['book_price_sale']:
                price_sale = int(re.sub(r' ', r'', item['book_price_sale']))
            else:
                price_sale = None
            # не нулевое ли значение rating
            if item['book_rating']:
                rating = float(re.sub(r',', r'.', item['book_rating']))
            else:
                rating = None

            authors = re.sub(r'\n', r'', item['book_authors'])
            authors = re.sub(r' ', r'', authors)

            new_item = {'book_id': int(re.findall(r'\d+', item['book_id'])[0]),
                        'book_name': item['book_name'],
                        'book_link': item['book_link'],
                        'book_authors': authors,
                        'book_price': price,
                        'book_price_sale': price_sale,
                        'book_rating': rating,
                        'update_at': datetime.now().strftime("%d.%m.%Y %H:%M")}
            collection = self.db[spider.name]
            book_id = new_item['book_id']
            collection.update_one({'book_id': book_id}, {'$set': new_item}, upsert=True)

        return item
