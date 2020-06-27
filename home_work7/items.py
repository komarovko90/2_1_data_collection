# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from scrapy.loader.processors import MapCompose, TakeFirst, Compose
import scrapy

def prepare_price(value):
    return int(value)

def prepare_specification(elem):
    return elem.strip()

def ready_dictionary(elem):
    temp_dict = {}
    for i in range(0, len(elem), 2):
        temp_dict[elem[i]] = elem[i+1]
    return temp_dict

class LeruaparsingItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
    product_params = scrapy.Field(input_processor=MapCompose(prepare_specification), output_processor=Compose(ready_dictionary))
    price = scrapy.Field(input_processor=MapCompose(prepare_price), output_processor=TakeFirst())
    photos = scrapy.Field()
