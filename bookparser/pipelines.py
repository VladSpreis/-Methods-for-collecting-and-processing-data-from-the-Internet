# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from itemadapter import ItemAdapter


class BookparserPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.vacancyBook24

    def process_item(self, item, spider):
        item['title'] = self.p_title(item['title'])
        item['author'] = self.p_author(item['author'])
        item['price_old'] = self.p_price(item['price_old'])
        item['price_new'] = self.p_price(item['price_new'])
        collection = self.mongobase[spider.name]
        collection.insert_one(item)
        return item

    def p_author(self, author):
        if author:
            return author.strip()
        else:
            return "No data"

    def p_rating(self, rating):
        if rating:
            return rating[0].strip()
        else:
            return "No data"

    def p_price(self, price):
        if price:
            return price.stip(),
        else:
            return "No data"

    def p_title(self, title):
        if title:
            return title.strip()
        else:
            return "No data"