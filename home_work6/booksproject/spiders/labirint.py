# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse        #Для подсказок объекта response
from booksproject.items import BooksprojectItem


class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/search/%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5/?stype=0']

    def parse(self, response: HtmlResponse):
        books_links = response.xpath("//a[@class='product-title-link']/@href").extract()
        for link in books_links:
            yield response.follow(link, callback=self.books_parse)
        next_page = response.xpath("//a[@title='Следующая']/@href").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def books_parse(self, response: HtmlResponse):
        link = response._url
        name = response.xpath("//div[@id='product-title']/h1/text()").extract_first()
        authors_block = response.xpath("//div[@class='product-description']//a[@data-event-label='author']/text()").extract() # /text()").extract_first()
        price = response.xpath("//span[@class='buying-price-val-number']/text()").extract_first()
        price_sale = None
        if not price:
            price = response.xpath("//span[@class='buying-priceold-val-number']/text()").extract_first()
            price_sale = response.xpath("//span[@class='buying-pricenew-val-number']/text()").extract_first()
        rating = response.xpath("//div[@id='rate']/text()").extract_first()
        book_id = response.xpath("//div[@class='articul']/text()").extract_first()
        yield BooksprojectItem(book_name=name, book_link=link, book_authors=authors_block, book_price=price,
                               book_price_sale=price_sale, book_rating=rating, book_id=book_id)


