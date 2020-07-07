from scrapy.crawler import CrawlerProcess           #Импортируем класс для создания процесса
from scrapy.settings import Settings                #Импортируем класс для настроек

from booksproject import settings                      #Наши настройки
from booksproject.spiders.labirint import LabirintSpider
from booksproject.spiders.book import Book24Spider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LabirintSpider)
    process.crawl(Book24Spider)

    process.start()
