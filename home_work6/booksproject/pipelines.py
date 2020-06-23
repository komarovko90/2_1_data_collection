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
        item['book_price'] = int(item['book_price'])
        item['book_price_sale'] = int(item['book_price_sale'])
        item['book_id'] = int(re.findall(r'\d+', item['book_id'])[0])
        item['book_rating'] = float(item['book_rating'])

        collection = self.db[spider.name]
        new_item = {'book_id': item['book_id'],
                    'book_name':  item['book_name'],
                    'book_link': item['book_link'],
                    'book_authors': item['book_authors'],
                    'book_price': item['book_price'],
                    'book_price_sale':item['book_price_sale'],
                    'book_rating': item['book_rating'],
                    'update_at': datetime.now().strftime("%d.%m.%Y %H:%M")}
        book_id = item['book_id']
        collection.update_one({'book_id': book_id}, {'$set': new_item}, upsert=True)

        return item
