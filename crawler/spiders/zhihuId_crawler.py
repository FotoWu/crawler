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
    name = "zhihuId"
    allowed_domains = ["zhihu.com"]
    start_urls = [
    ]
    base_url = "https://www.zhihu.com"
    basic_information = {}
    following_users = []
    follower_users = []
    MAX_CRAWL_USERS = 40
    MAX_CRAWL_QUESTIONS = 40
    MAX_COMMENT_NUM = 40
    post_num = answer_num = follower_num = following_num = 0

    def start_requests(self):
        yield Request(url="https://www.zhihu.com/people/zhang-jia-wei/",
                      callback=self.parse_basic_information)
        yield Request(url="https://www.zhihu.com/people/excited-vczh/",
                      callback=self.parse_basic_information)
        yield Request(url="https://www.zhihu.com/people/chu-yang-51-32/",
                      callback=self.parse_basic_information)
        yield Request(url="https://www.zhihu.com/people/sgai/",
                      callback=self.parse_basic_information)
        yield Request(url="https://www.zhihu.com/people/SemitLee/",
                      callback=self.parse_basic_information)
        yield Request(url="https://www.zhihu.com/people/jieducm/",
                      callback=self.parse_basic_information)
        yield Request(url="https://www.zhihu.com/people/chen-guang-55/",
                      callback=self.parse_basic_information)
        yield Request(url="https://www.zhihu.com/people/yuhang-liu-34/",
                      callback=self.parse_basic_information)
        yield Request(url="https://www.zhihu.com/people/chibaole/",
                      callback=self.parse_basic_information)
        yield Request(url="https://www.zhihu.com/people/wang-rui-en/",
                      callback=self.parse_basic_information)

    def add_following_pages(self, base_url):
        crawl_urls = []
        total_pages = self.MAX_CRAWL_USERS // 20
        for page in range(total_pages):
            params = {"page": page+1}
            current_num = (page+1) * 20
            url = base_url + 'following?' + urlencode(params)
            if current_num < self.following_num:
                crawl_urls.append(url)
            url = base_url + 'followers?' + urlencode(params)
            if current_num < self.follower_num:
                crawl_urls.append(url)

        total_pages = self.MAX_CRAWL_QUESTIONS // 20
        for page in range(total_pages):
            params = {"page": page+1}
            current_num = (page+1) * 20
            url = base_url + 'answers?' + urlencode(params)
            if current_num < self.answer_num:
                crawl_urls.append(url)
            url = base_url + 'posts?' + urlencode(params)
            if current_num < self.post_num:
                crawl_urls.append(url)
        return crawl_urls

    def parse_basic_information(self, response):
        # # 获得基本信息
        user_item = UserItem()
        print("正在爬取", response.url)
        soup = BeautifulSoup(response.body)
        user_name = soup.find('span', 'ProfileHeader-name').text
        user_signature = soup.find('span', 'ProfileHeader-headline').text
        print(user_name, user_signature)
        user_item['name'] = user_name
        user_item['signature'] = user_signature
        profile_items = soup.find_all('div', 'ProfileHeader-detailItem')
        label_list = ['settlement', 'industry', 'work_experience', 'education_experience', 'personal_profile']
        for index, profile_item in enumerate(profile_items):
            detail_label = profile_item.find('span').text
            detail_value = profile_item.find('div').text
            user_item[label_list[index]] = detail_value
            print(detail_label, ':', detail_value)

        # 回答-想法 关注数 粉丝数
        tab_items = soup.find('ul', 'ProfileMain-tabs').find_all(
            lambda tag: tag.name == 'li' and tag.get('class') == ['Tabs-item'])
        tab_label_list = ['answer_num', 'question_num', 'post_num', 'column_num',
                          'thinking_num']
        for index, tab_item in enumerate(tab_items):
            if 'Tabs-item--noMeta' in tab_item['class']:
                continue
            label = tab_item.a.find(text=True, recursive=False).next_element
            value = tab_item.a.span.text
            user_item[tab_label_list[index]] = value
            print(label, ':', value)
        tab_label_list = ['following_num', 'follower_num']
        for index, number_board_item in enumerate(soup.find_all('a', {'class', 'Button NumberBoard-item Button--plain'})):
            label = number_board_item.div.div.text
            value = number_board_item.div.div.next_sibling.text
            user_item[tab_label_list[index]] = value
            print(label, ":", value)

        follow_ship_card = soup.find('div', 'FollowshipCard')
        self.following_num = int(re.sub('\D', '', user_item['following_num']))
        self.follower_num = int(re.sub('\D', '', user_item['follower_num']))
        self.answer_num = int(re.sub('\D', '', soup.find('li', {'aria-controls': 'Profile-answers'}).span.text))
        self.post_num = int(re.sub(r'\D', '', soup.find('li', {'aria-controls': 'Profile-posts'}).span.text))
        print(self.follower_num, self.following_num, self.answer_num, self.post_num)
        crawl_urls = self.add_following_pages(response.url)

        # 爬取start_urls
        for url in crawl_urls:
            yield self.make_requests_from_url(url=url)
        yield user_item

    def parse(self, response):
        if "following" in response.url:
            yield from self.parse_followings(response)
        elif "follower" in response.url:
            yield from self.parse_followers(response)
        elif "answers" in response.url:
            yield from self.parse_answers(response)
        elif "posts" in response.url:
            yield from self.parse_posts(response)

    def parse_followings(self, response):
        print("正在爬取", response.url)
        soup = BeautifulSoup(response.body)
        user_name = soup.find('span', 'ProfileHeader-name').text
        following_user_names = soup.find_all('span', 'UserItem-name')
        for following_user_name in following_user_names:
            self.following_users.append(following_user_name.text)
            follow_list = FollowingListItem(user_name=user_name, follow_name=following_user_name.text)
            yield follow_list

    def parse_followers(self, response):
        print("正在爬取", response.url)
        soup = BeautifulSoup(response.body)
        user_name = soup.find('span', 'ProfileHeader-name').text
        follower_user_names = soup.find_all('span', 'UserItem-name')
        for follower_user_name in follower_user_names:
            self.follower_users.append(follower_user_name.text)
            follow_list = FollowingListItem(user_name=follower_user_name.text, follow_name=user_name)
            yield follow_list

    def parse_answers(self, response):
        print("正在爬取", response.url)
        soup = BeautifulSoup(response.body)
        list_items = soup.find('div', 'Profile-answers').find_all('div', 'List-item')
        for item in list_items:
            title_element = item.find('a', {'data-za-detail-view-element_name': 'Title'})
            title = title_element.text
            title_href = urljoin(self.base_url, title_element['href'])
            content = item.find('span', 'RichText').text
            up_num = item.find('button', 'VoteButton--up').text
            comment_num = item.find('div', 'ContentItem-actions').button.text
            answer_item = AnswerItem(title=title, title_href=title_href, content=content,
                                     up_num=up_num, comment_num=comment_num)
            yield answer_item

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
        driver = webdriver.PhantomJS(executable_path='/Users/linsp/Downloads/phantomjs-2.1-2.1-macosx/bin/phantomjs')
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
