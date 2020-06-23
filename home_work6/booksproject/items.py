# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BooksprojectItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    book_name = scrapy.Field()
    book_link = scrapy.Field()
    book_authors = scrapy.Field()
    book_price = scrapy.Field()
    book_price_sale = scrapy.Field()
    book_rating = scrapy.Field()
    book_id = scrapy.Field()
