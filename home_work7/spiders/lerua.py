import scrapy
from scrapy.http import HtmlResponse
from leruaparsing.items import LeruaparsingItem
from scrapy.loader import ItemLoader

class LeruaSpider(scrapy.Spider):
    name = 'lerua'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search):
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}']

    def parse(self, response: HtmlResponse):
        items = response.xpath("//div[@class='ui-sorting-cards']/div/div/@data-product-url").extract()
        for item in items:
            yield response.follow(item, callback=self.product_parse)

        next_page = response.xpath("//div[@class='service-panel-wrapper']//div[@class='next-paginator-button-wrapper']/a/@href").extract_first()
        yield response.follow(next_page, callback=self.parse)

    def product_parse(self, response: HtmlResponse):
        loader = ItemLoader(item=LeruaparsingItem(), response=response)
        loader.add_value('link', response.url)
        loader.add_xpath('name', "//h1[@slot='title']/text()")
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath('product_params', "//div[@class='def-list__group']/dt/text() | //div[@class='def-list__group']/dd/text()")
        loader.add_xpath('photos', "//picture[@slot='pictures']/source[1]/@srcset")
        yield loader.load_item()
