# -*- coding: utf-8 -*-

import logging
from time import sleep
from urllib.parse import unquote
import scrapy
from selenium import webdriver
from selenium.webdriver.remote.remote_connection import LOGGER

from crawler.items import \
    SearchContentItem, SearchContentCommentItem
from crawler.settings import PhantomJS_PATH

LOGGER.setLevel(logging.WARNING)


class DmozSpider(scrapy.spiders.CrawlSpider):
    name = "zhihuSearch"
    allowed_domains = ["zhihu.com"]
    start_urls = [
        "https://www.zhihu.com/search?type=content&q=%E8%AE%A1%E7%AE%97%E6%9C%BA",
        "https://www.zhihu.com/search?type=content&q=%E8%BD%AF%E4%BB%B6%E5%B7%A5%E7%A8%8B",
        "https://www.zhihu.com/search?type=content&q=%E9%9C%80%E6%B1%82%E5%88%86%E6%9E%90",
        "https://www.zhihu.com/search?type=content&q=%E8%BD%AF%E4%BB%B6%E6%B5%8B%E8%AF%95",
        "https://www.zhihu.com/search?type=content&q=%E6%B5%99%E6%B1%9F%E5%A4%A7%E5%AD%A6",
        "https://www.zhihu.com/search?type=content&q=%E7%88%AC%E8%99%AB",
        "https://www.zhihu.com/search?type=content&q=%E8%87%AA%E5%8A%A8%E5%8C%96%E6%B5%8B%E8%AF%95",
        "https://www.zhihu.com/search?type=content&q=%E6%B5%8B%E8%AF%95%E7%94%A8%E4%BE%8B",
        "https://www.zhihu.com/search?type=content&q=%E9%A1%B9%E7%9B%AE%E7%AE%A1%E7%90%86",
        "https://www.zhihu.com/search?type=content&q=%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84",
    ]
    #知乎一次搜索拉到底也只有200条
    MAX_CRAWL_CONTENT = 500

    def parse(self, response):
        yield from self.parse_content(response)

    def parse_content(self, response):
        comment_id = 1
        driver = webdriver.PhantomJS(executable_path=PhantomJS_PATH)
        driver.get(response.url)
        sleep(1)
        # 去除话题部分
        driver.execute_script(
            """
            topElements = document.getElementsByClassName(
                'Card SearchSections'
            );
            topElements[0].remove()"""
        )
        # 下拉页面至搜索结果数量足够
        total_pages = (self.MAX_CRAWL_CONTENT + 4) // 10
        print("正在爬取", response.url)
        for page in range(total_pages):
            driver.execute_script("""
                height = document.documentElement.scrollHeight
                    || document.body.scrollHeight;
                window.scrollTo(0, height);""")
            print("正在爬取第", page + 1, "页")
            sleep(1)
        # 提取所需数据
        content_items = driver.find_elements_by_class_name("AnswerItem")[0:self.MAX_CRAWL_CONTENT]
        for item in content_items:
            title = item.find_element_by_tag_name('span').text
            title_href = item.find_element_by_tag_name("a").get_property("href")
            author = item.find_element_by_tag_name("b").text
            vote_num = item.find_element_by_class_name("VoteButton").text
            comment_num = item.find_element_by_class_name("ContentItem-action").text
            post_item = SearchContentItem(id=comment_id,
                                          keyword=unquote(response.url.strip("https://www.zhihu.com/search?type=content&q=")),
                                          title=title, title_href=title_href,
                                          author=author, vote_num=vote_num, comment_num=comment_num)
            yield post_item
            # 定位评论按钮，点击后提取评论列表
            button = item.find_element_by_class_name("ContentItem-action")
            button.click()
            sleep(1)
            comment_items = driver.find_elements_by_class_name("CommentItem")
            for comment_item in comment_items:
                comment_author = comment_item.find_element_by_class_name("UserLink-avatar").get_property("alt")
                comment_content = comment_item.find_element_by_class_name("CommentItem-content").text
                post_item = SearchContentCommentItem(id=comment_id, author=comment_author, content=comment_content,
                                                     keyword=unquote(response.url.strip("https://www.zhihu.com/search?type=content&q=")))
                yield post_item
            button.click()
            sleep(1)
            comment_id += 1
        driver.close()
