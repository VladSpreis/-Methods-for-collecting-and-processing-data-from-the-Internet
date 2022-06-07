from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging

from bookparser.spiders.book24 import Book24Spider

if __name__ == "__main__":
    configure_logging()
    settings = get_project_settings()
    runner = CrawlerRunner(settings)
    runner.crawl(Book24Spider)

    reactor.run()
