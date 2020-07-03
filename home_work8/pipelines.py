# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
import scrapy


class InstaparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['hh_db']

    def process_item(self, item, spider):
        collection = self.db[spider.name]
        # добавление в БД, отсеивая по сочетанию  user_id  и following_id/follower_id
        collection.replace_one({'follow_id': item['follow_id'], 'user_id': item['user_id'], 'type_field': item['type_field']},
                               item,
                               upsert=True)
        return item

'''
Для поиска всех подписок конкретного пользователя:
collection.find({'user_name': '_kolpa__', 'type_field': 'following'})

Для поиска всех подписчиков конкретного пользователя:
collection.find({'user_name': '_kolpa__', 'type_field': 'follower'})
'''

class InstaPhotoPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['follow_photo']:
            try:
                yield scrapy.Request(item['follow_photo'], meta=item)
            except Exception as e:
                print(e)

    def item_completed(self, results, item, info):
        if results:
            image = {}
            if results[0][0]:
                image['url'] = results[0][1]['url']
                image['path'] = results[0][1]['path']
            item['follow_photo'] = image
        return item

    def file_path(self, request, response=None, info=None):
        item = request.meta
        return item['user_name'] + '/' + item['type_field'] + '/' + item['follow_id'] + '_' + item['follow_name'] + '.jpg'