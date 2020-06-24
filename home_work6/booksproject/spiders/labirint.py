# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse        #Для подсказок объекта response
from booksproject.items import BooksprojectItem

class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/search/%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5/?stype=0']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@title='Следующая']/@href").extract_first()

        books_links = response.xpath("//a[@class='product-title-link']/@href").extract()
        for link in books_links:
            yield response.follow(link, callback=self.books_parse)

        yield response.follow(next_page, callback=self.parse)

    def books_parse(self, response: HtmlResponse):
        link = response._url
        name = response.xpath("//div[@id='product-title']/h1/text()").extract_first()
        authors_block = response.xpath("//div[@class='product-description']//a[@data-event-label='author']") # /text()").extract_first()
        authors_name = ''
        for author in authors_block:
            authors_name = authors_name + ' ' + author.xpath("./text()").extract_first()
        price = response.xpath("//span[@class='buying-priceold-val-number']/text()").extract_first()
        price_sale = response.xpath("//span[@class='buying-pricenew-val-number']/text()").extract_first()
        rating = response.xpath("//div[@id='rate']/text()").extract_first()
        book_id = response.xpath("//div[@class='articul']/text()").extract_first()
        yield BooksprojectItem(book_name=name, book_link=link, book_authors=authors_name, book_price=price,
                               book_price_sale=price_sale, book_rating=rating, book_id=book_id)


class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/search/?q=%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5']

    def parse(self, response: HtmlResponse):
        pages = response.xpath("//div[contains(@class, 'catalog-pagination__list')]/a")

        books_links = response.xpath("//div[@class='catalog-products__item js-catalog-products-item']//a[@class='book__title-link js-item-element ddl_product_link ']/@href").extract()
        for link in books_links:
            yield response.follow(link, callback=self.books_parse)

        for page in pages:
            if page.xpath("./text()").extract_first() == 'Далее':
                yield response.follow(page.xpath("./@href").extract_first(), callback=self.parse)


    def books_parse(self, response: HtmlResponse):
        link = response._url
        name = response.xpath("//h1[@class='item-detail__title']/text()").extract_first()

        item_list = response.xpath("//div[@class='item-tab__chars-list']/*")
        for item in item_list:
            if item.xpath("./span[@class='item-tab__chars-key']"):  # проверяем наличие блока span
                name_item = item.xpath("./span[@class='item-tab__chars-key']/text()").extract_first()
                if name_item == 'Автор:':  # проверяем наличие нужной нам позиции
                    if item.xpath("./span[@class='item-tab__chars-value']/a"):  # проверяем на наличии тэга a
                        authors_block = item.xpath("./span[@class='item-tab__chars-value']/a")
                        author_list = []
                        for author in authors_block:
                            author_list.append(author.xpath("./text()").extract_first())
                        authors_name = ', '.join(author_list)
                    else:  # иначе тэге span
                        authors_name = item.xpath("./span[@class='item-tab__chars-value']/text()").extract_first()
                elif name_item == 'Артикул:':
                    book_id = item.xpath("./span[@class='item-tab__chars-value']/text()").extract_first()
        price = response.xpath("//div[@class='item-actions__price-old']/text()").extract_first()
        price_sale = response.xpath("//div[@class='item-actions__prices']//b/text()").extract_first()
        rating = response.xpath("//span[@class='rating__rate-value']/text()").extract_first()
        yield BooksprojectItem(book_name=name, book_link=link, book_authors=authors_name, book_price=price,
                               book_price_sale=price_sale, book_rating=rating, book_id=book_id)