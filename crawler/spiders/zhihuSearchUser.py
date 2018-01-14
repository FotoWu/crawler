from scrapy.http import Request
from crawler.items import *
import re
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from selenium import webdriver
from crawler.settings import PhantomJS_PATH
from time import sleep


class DmozSpider(scrapy.spiders.CrawlSpider):
    name = "zhihuSearchUser"
    allowed_domains = ["zhihu.com"]
    start_urls = [
        "https://www.zhihu.com/search?type=people&q=%E7%8B%97",
        #"https://www.zhihu.com/search?type=people&q=%E7%8C%AB",
        #"https://www.zhihu.com/search?type=people&q=%E4%BA%BA",
        #"https://www.zhihu.com/search?type=people&q=%E5%A4%A9",
        #"https://www.zhihu.com/search?type=people&q=%E5%9C%B0",
        #"https://www.zhihu.com/search?type=people&q=%E6%B0%B4",
        #"https://www.zhihu.com/search?type=people&q=%E7%81%AB",
        #"https://www.zhihu.com/search?type=people&q=%E7%94%B5",
        #"https://www.zhihu.com/search?type=people&q=%E5%85%89",
        #"https://www.zhihu.com/search?type=people&q=%E8%83%BD",
    ]
    base_url = "https://www.zhihu.com"
    MAX_CRAWL_CONTENT = 50
    MAX_CRAWL_USERS = 100
    MAX_COMMENT_NUM = 50
    post_num = answer_num = follower_num = following_num = 0

    def start_requests(self):
        driver = webdriver.PhantomJS(executable_path=PhantomJS_PATH)
        for url in self.start_urls:
            driver.get(url)
            sleep(1)
            # 下拉页面至搜索结果数量足够
            total_pages = (self.MAX_CRAWL_CONTENT + 4) // 10
            print("正在爬取", url)
            for page in range(total_pages):
                driver.execute_script("""
                           height = document.documentElement.scrollHeight
                               || document.body.scrollHeight;
                           window.scrollTo(0, height);""")
                print("正在爬取第", page + 1, "页")
                sleep(1)
            # 提取所需数据
            content_items = driver.find_elements_by_class_name("ContentItem-image")[0:self.MAX_CRAWL_CONTENT]
            for item in content_items:
                url = item.find_element_by_class_name("UserLink-link").get_property("href")
                yield Request(url=url, callback=self.parse_basic_information)

    def add_following_pages(self, base_url):
        crawl_urls = []
        total_pages = self.MAX_CRAWL_USERS // 20
        for page in range(total_pages):
            params = {"page": page+1}
            current_num = (page+1) * 20
            url = base_url + '/following?' + urlencode(params)
            if current_num < self.following_num:
                crawl_urls.append(url)
            url = base_url + '/followers?' + urlencode(params)
            if current_num < self.follower_num:
                crawl_urls.append(url)
        return crawl_urls

    def parse(self, response):
        # pass
        if "following" in response.url:
            yield from self.parse_followings(response)
        elif "follower" in response.url:
            yield from self.parse_followers(response)

    def parse_basic_information(self, response):
        # # 获得基本信息
        user_item = SearchUserItem()
        print("正在爬取", response.url)
        soup = BeautifulSoup(response.body,"lxml")
        user_name = soup.find('span', 'ProfileHeader-name').text
        user_signature = soup.find('span', 'ProfileHeader-headline').text
        # print(user_name, user_signature)
        user_item['name'] = user_name
        user_item['signature'] = user_signature
        profile_items = soup.find_all('div', 'ProfileHeader-detailItem')
        label_list = ['settlement', 'industry', 'work_experience', 'education_experience', 'personal_profile']
        for index, profile_item in enumerate(profile_items):
            detail_value = profile_item.find('div').text
            user_item[label_list[index]] = detail_value

        # 回答-想法 关注数 粉丝数
        tab_items = soup.find('ul', 'ProfileMain-tabs').find_all(
            lambda tag: tag.name == 'li' and tag.get('class') == ['Tabs-item'])
        tab_label_list = ['answer_num', 'question_num', 'post_num', 'column_num',
                          'thinking_num']
        for index, tab_item in enumerate(tab_items):
            if 'Tabs-item--noMeta' in tab_item['class']:
                continue
            value = tab_item.a.span.text
            user_item[tab_label_list[index]] = value

        tab_label_list = ['following_num', 'follower_num']
        for index, number_board_item in enumerate(soup.find_all('a', {'class', 'Button NumberBoard-item Button--plain'})):
            value = number_board_item.div.div.next_sibling.text
            user_item[tab_label_list[index]] = value

        self.following_num = int(re.sub('\D', '', user_item['following_num']))
        self.follower_num = int(re.sub('\D', '', user_item['follower_num']))
        self.answer_num = int(re.sub('\D', '', soup.find('li', {'aria-controls': 'Profile-answers'}).span.text))
        self.post_num = int(re.sub(r'\D', '', soup.find('li', {'aria-controls': 'Profile-posts'}).span.text))
        # print(self.follower_num, self.following_num, self.answer_num, self.post_num)
        crawl_urls = self.add_following_pages(response.url)
        #
        # 爬取start_urls
        for url in crawl_urls:
            yield self.make_requests_from_url(url=url)
        yield user_item

    def parse_followings(self, response):
        print("正在爬取", response.url)
        soup = BeautifulSoup(response.body)
        user_name = soup.find('span', 'ProfileHeader-name').text
        following_user_names = soup.find_all('span', 'UserItem-name')
        for following_user_name in following_user_names:
            follow_list = SearchFollowingListItem(user_name=user_name, follow_name=following_user_name.text)
            yield follow_list

    def parse_followers(self, response):
        print("正在爬取", response.url)
        soup = BeautifulSoup(response.body)
        user_name = soup.find('span', 'ProfileHeader-name').text
        follower_user_names = soup.find_all('span', 'UserItem-name')
        for follower_user_name in follower_user_names:
            follow_list = SearchFollowingListItem(user_name=follower_user_name.text, follow_name=user_name)
            yield follow_list


