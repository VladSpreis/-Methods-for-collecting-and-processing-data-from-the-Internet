import itemloaders
import scrapy
from scrapy.http import HtmlResponse
from castparser.items import CastparserItem
from  scrapy.loader import ItemLoader

class CastoramaSpider(scrapy.Spider):
    name = 'castorama'
    allowed_domains = ['castorama.ru']
    start_urls = ["https://www.castorama.ru/catalogsearch/result/?q=%D0%BA%D1%80%D0%B0%D1%81%D0%BA%D0%B0"]


    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@class='next i-next']/@href").get()
        if next_page:
            yield response.follow(next_page,callback=self.parse)
        links = response.xpath("//a[@class='product-card__img-link']")
        for link in links:
            yield response.follow(link, callback=self.parse_add)




    def parse_add(self, response:HtmlResponse):
        loader = ItemLoader(item=CastparserItem(), response=response)
        loader.add_xpath('title', "//h1/text()")
        loader.add_xpath('price', "//div[@class ='add-to-cart__price js-fixed-panel-trigger']//span[@class='price']//text()")
        loader.add_value('url', response.url)
        loader.add_value('photos', "//li[contains(@class, 'top-slide swiper-slide')]/div/img/@data-src")
        yield loader.load_item()










