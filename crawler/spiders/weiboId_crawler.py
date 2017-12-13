import scrapy
from bs4 import BeautifulSoup


class WeiboSpider(scrapy.spiders.CrawlSpider):
    name = "weiboId"
    allowed_domains = ["weibo.com"]
    start_urls = [
        "https://weibo.com/5746403289/Fzco8rkY1?ref=feedsdk&type=comment#_rnd1513046280799",
    ]

    def parse(self, response):
        soup = BeautifulSoup(response.body)

