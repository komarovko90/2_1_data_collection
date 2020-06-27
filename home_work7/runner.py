from scrapy.crawler import CrawlerProcess           #Импортируем класс для создания процесса
from scrapy.settings import Settings                #Импортируем класс для настроек

from leruaparsing import settings                      #Наши настройки
from leruaparsing.spiders.lerua import LeruaSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeruaSpider, search='краска')

    process.start()
