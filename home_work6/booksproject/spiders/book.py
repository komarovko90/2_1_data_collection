import scrapy
from scrapy.http import HtmlResponse        #Для подсказок объекта response
from booksproject.items import BooksprojectItem


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
        authors = None
        for item in item_list:
            if item.xpath("./span[@class='item-tab__chars-key']/text()").extract_first() == 'Артикул:':
                book_id = item.xpath("./span[@class='item-tab__chars-value']/text()").extract_first()
            if item.xpath("./span[@class='item-tab__chars-key']/text()").extract_first() == 'Автор:':
                authors = item.xpath("./span[@class='item-tab__chars-value']/text() | ./span[@class='item-tab__chars-value']/a/text()").extract()
        price = response.xpath("//div[@class='item-actions__price-old']/text()").extract_first()
        price_sale = response.xpath("//div[@class='item-actions__prices']//b/text()").extract_first()
        rating = response.xpath("//span[@class='rating__rate-value']/text()").extract_first()
        yield BooksprojectItem(book_name=name, book_link=link, book_authors=authors, book_price=price,
                               book_price_sale=price_sale, book_rating=rating, book_id=book_id)
