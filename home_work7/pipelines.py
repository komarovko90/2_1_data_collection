# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient

class LeruaparsingPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['hh_db']

    def process_item(self, item, spider):
        collection = self.db[spider.name]
        link = item['link']
        collection.update_one({'link': link}, {'$set': item}, upsert=True)
        return item

class LeruaPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for image in item["photos"]:
                try:
                    yield scrapy.Request(image, meta=item)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
           item['photos'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None):
        item = request.meta
        return item['name'] + '/'+ os.path.basename(request.url)