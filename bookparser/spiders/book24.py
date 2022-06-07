import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem





class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']
    genres = 'романы'
    num_page = 1
    start_urls = [f"https://book24.ru/search/page-{num_page}/?q={genres}"]

    def parse(self, response):
        Book24Spider.num_page += 1
        next_page = f"https://book24.ru/search/page-{Book24Spider.num_page}/?q={Book24Spider.genres}"
        if response.status != 404:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//div[@class='product-list__item']//a/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.parse_book)


    def parse_book(self, response: HtmlResponse):
        title = response.xpath("//div/h1[@itemprop='name']/text()").get()
        author = response.xpath("//li[@class='product-characteristic__item-holder' and position()=1]//a/text()").get()
        if author != response.xpath("//li[@class='product-characteristic__item-holder' and position()=1]//a/text()").get():
            author = response.xpath("//li[@class='product-characteristic__value']//div").get()
        old_price = response.xpath("//div/span[@class='app-price product-sidebar-price__price-old']/text()").get()
        new_price = response.xpath("//div/span[@class='app-price product-sidebar-price__price']/text()").get()
        rating = response.xpath("//span[@class='rating-widget__main-text']/text()").getall()
        url = response.url
        yield BookparserItem(title=title, author=author, price_old=old_price, price_new=new_price, rating=rating, url=url)