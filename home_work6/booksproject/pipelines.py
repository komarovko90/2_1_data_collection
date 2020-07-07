# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import re
from pymongo import MongoClient
from datetime import datetime
from pprint import pprint


class BooksprojectPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['hh_db']

    def prepare_item_labirint(self, item):
        item['book_authors'] = ', '.join(item['book_authors'])
        item['book_id'] = int(re.findall(r'\d+', item['book_id'])[0])
        item['update_at'] = datetime.now().strftime("%d.%m.%Y %H:%M")
        if item['book_price']:
            item['book_price'] = int(item['book_price'])
        if item['book_price_sale']:
            item['book_price_sale'] = int(item['book_price_sale'])
        if item['book_rating']:
            item['book_rating'] = float(item['book_rating'])

    def prepare_item_book(self, item):
        item['update_at'] = datetime.now().strftime("%d.%m.%Y %H:%M")
        item['book_id'] = int(re.findall(r'\d+', item['book_id'])[0])
        # не нулевое ли значение price
        if item['book_price']:
            price = re.sub(r' ', r'', item['book_price'])
            price = int(re.findall(r'\d+', price)[0])
            item['book_price'] = price

        # не нулевое ли значение price_sale
        if item['book_price_sale']:
            price_sale = int(re.sub(r' ', r'', item['book_price_sale']))
            item['book_price_sale'] = price_sale

        # не нулевое ли значение rating
        if item['book_rating']:
            rating = float(re.sub(r',', r'.', item['book_rating']))
            item['book_rating'] = rating

        # не нулевое ли значение book_authors
        if item['book_authors']:
            author_list = []
            for author in item['book_authors']:
                my_str = author.strip()
                if my_str:
                    author_list.append(author.strip())
            authors = ', '.join(author_list)
            item['book_authors'] = authors

    def process_item(self, item, spider):
        if spider.name == 'labirint':
            self.prepare_item_labirint(item)
        elif spider.name == 'book24':
            self.prepare_item_book(item)

        collection = self.db[spider.name]
        collection.replace_one({'book_id': item['book_id']}, item, upsert=True)
        return item
