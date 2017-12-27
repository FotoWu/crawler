import scrapy
from scrapy.http import Request
from crawler.items import *
import re
from bs4 import BeautifulSoup
from urllib.parse import urlencode, urljoin


class DmozSpider(scrapy.spiders.CrawlSpider):
    name = "zhihuId_answer"
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
        return crawl_urls

    def parse_basic_information(self, response):
        # # 获得基本信息
        user_item = UserItem()
        print("正在爬取", response.url)
        soup = BeautifulSoup(response.body)
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
            # print(detail_label, ':', detail_value)

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
            # print(label, ':', value)
        tab_label_list = ['following_num', 'follower_num']
        for index, number_board_item in enumerate(soup.find_all('a', {'class', 'Button NumberBoard-item Button--plain'})):
            value = number_board_item.div.div.next_sibling.text
            user_item[tab_label_list[index]] = value
            # print(label, ":", value)

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

    def parse(self, response):
        # pass
        if "following" in response.url:
            yield from self.parse_followings(response)
        elif "follower" in response.url:
            yield from self.parse_followers(response)
        elif "answers" in response.url:
            yield from self.parse_answers(response)

    def parse_followings(self, response):
        print("正在爬取", response.url)
        soup = BeautifulSoup(response.body)
        user_name = soup.find('span', 'ProfileHeader-name').text
        following_user_names = soup.find_all('span', 'UserItem-name')
        for following_user_name in following_user_names:
            follow_list = FollowingListItem(user_name=user_name, follow_name=following_user_name.text)
            yield follow_list

    def parse_followers(self, response):
        print("正在爬取", response.url)
        soup = BeautifulSoup(response.body)
        user_name = soup.find('span', 'ProfileHeader-name').text
        follower_user_names = soup.find_all('span', 'UserItem-name')
        for follower_user_name in follower_user_names:
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
