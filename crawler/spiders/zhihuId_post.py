import scrapy
from bs4 import BeautifulSoup
from scrapy.http import Request
from urllib.parse import urlencode, urljoin
from selenium import webdriver
import time
import re
from selenium.webdriver.remote.remote_connection import LOGGER
import logging
from crawler.items import \
    UserItem, FollowingListItem, AnswerItem, PostItem, PostCommentItem

LOGGER.setLevel(logging.WARNING)


class DmozSpider(scrapy.spiders.CrawlSpider):
    name = "zhihuId_post"
    allowed_domains = ["zhihu.com"]
    start_urls = [
        "https://www.zhihu.com/people/zhang-jia-wei/",
        "https://www.zhihu.com/people/excited-vczh/",
        "https://www.zhihu.com/people/chu-yang-51-32/",
        "https://www.zhihu.com/people/sgai/",
        "https://www.zhihu.com/people/SemitLee/",
        "https://www.zhihu.com/people/jieducm/",
        "https://www.zhihu.com/people/chen-guang-55/",
        "https://www.zhihu.com/people/yuhang-liu-34/",
        "https://www.zhihu.com/people/chibaole/",
        "https://www.zhihu.com/people/wang-rui-en/",
    ]
    base_url = "https://www.zhihu.com"
    MAX_CRAWL_USERS = 100
    MAX_CRAWL_QUESTIONS = 500
    MAX_COMMENT_NUM = 50
    post_num = answer_num = follower_num = following_num = 0

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse_basic_information)

    def add_following_pages(self, base_url):
        crawl_urls = []
        total_pages = self.MAX_CRAWL_QUESTIONS // 20
        for page in range(total_pages):
            params = {"page": page + 1}
            current_num = (page + 1) * 20
            url = base_url + 'posts?' + urlencode(params)
            if current_num < self.post_num:
                crawl_urls.append(url)
        return crawl_urls

    def parse_basic_information(self, response):
        # # 获得基本信息
        soup = BeautifulSoup(response.body)
        self.post_num = int(re.sub(r'\D', '', soup.find('li', {'aria-controls': 'Profile-posts'}).span.text))
        # print(self.follower_num, self.following_num, self.answer_num, self.post_num)
        crawl_urls = self.add_following_pages(response.url)
        #
        # 爬取start_urls
        for url in crawl_urls:
            yield Request(url=url, callback=self.parse_posts)

    def parse_posts(self, response):
        print("正在爬取", response.url)
        soup = BeautifulSoup(response.body)
        list_items = soup.find('div', {"id": "Profile-posts"}).find_all('div', 'List-item')
        for item in list_items:
            title_element = item.find('a', {'data-za-detail-view-element_name': 'Title'})
            title = title_element.text
            title_href = urljoin(self.base_url, title_element['href'])
            content = item.find('span', 'RichText').text
            up_num = item.find('button', 'LikeButton').text
            comment_num = item.find('div', 'ContentItem-actions').find('button', 'Button--withIcon').text
            post_item = PostItem(
                title=title, title_href=title_href, content=content, up_num=up_num, comment_num=comment_num)
            yield post_item
        yield from self.parse_post_comment(response.url)

    # 爬取一个post界面的comment
    def parse_post_comment(self, url):
        print("评论操作")
        # driver = webdriver.PhantomJS(executable_path='/Users/linsp/Downloads/phantomjs-2.1-2.1-macosx/bin/phantomjs')
        driver = webdriver.PhantomJS(executable_path='G:\\vagrant\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe')
        driver.get(url)
        time.sleep(0.5)
        for post in driver.find_elements_by_xpath("//div[@id='Profile-posts']//div[@class='List-item']"):
            post_title = post.find_element_by_xpath(".//a[@data-za-detail-view-element_name='Title']").text
            comment_button = post.find_element_by_xpath(".//div[@class='ContentItem-actions']/button[contains(@class, 'Button--withIcon')]")
            comment_num = int(re.findall("\d+", comment_button.text)[0])
            comment_page_num = (comment_num-1) // 20
            comment_button.click()
            time.sleep(0.5)
            current_comment_num = 0
            current_comment_page_num = 0
            comment_num = min(comment_num, self.MAX_COMMENT_NUM)
            while current_comment_num < comment_num:
                comment_items = post.find_elements_by_xpath(
                    ".//div[@class='Comments-container']//div[@class='CommentItem']")
                for comment_item in comment_items:
                    if current_comment_num >= comment_num:
                        break
                    current_comment_num += 1
                    comment_text = "\n".join(comment_item.text.split("\n")[0:-1])
                    post_comment_item = PostCommentItem(post_title=post_title, comment_text=comment_text)
                    yield post_comment_item
                if current_comment_page_num < comment_page_num:
                    current_comment_page_num += 1
                    next_button = post.find_element_by_xpath(".//button[contains(@class, 'PaginationButton-next')]")
                    next_button.click()
                    time.sleep(0.5)
            print(current_comment_num, '\n')