# -*- coding: utf-8 -*-
from scrapy.http import Request
from bs4 import BeautifulSoup
from selenium.webdriver.remote.remote_connection import LOGGER
import logging
import time
import re
from selenium import webdriver
from crawler.items import *
from crawler.settings import PhantomJS_PATH

LOGGER.setLevel(logging.WARNING)
username = '13221699880'
password = 'diaodiao187188'
service_args = ['--load-images=no', '--disk-cache=yes', '--ignore-ssl-errors=true']
driver = webdriver.PhantomJS(executable_path=PhantomJS_PATH, service_args=service_args)


class WeibotopicSpider(scrapy.Spider):

    MAX_CRAWL_FOLLOWERS = 100
    MAX_CRAWL_POSTS = 500
    MAX_CRAWL_COMMENTS = 50

    name = 'weibotopic'
    allowed_domains = ['weibo.com']
    start_urls = [
        'https://weibo.com/p/100808e997c2717e923f63720fc0b80a765151',
        # 'https://weibo.com/p/100808df20415fc85ebbd132fdf07c97d45437',
        # 'https://weibo.com/p/1008080fe02c6f98283838ed83f3f254db3866',
        # 'https://weibo.com/p/1008087cd7f124bf170094f80b537397c40e58',
        # 'https://weibo.com/p/1008080c3a86460c362cba0d8593b52916b404',
        # 'https://weibo.com/p/10080841499d7aa6e70f6d16a4274f9d3e1b87',
        # 'https://weibo.com/p/1008085d82c934b97e5cef62b0ed6ab7adc813'
        # 'https://weibo.com/p/1008088c1c0f3885a9122634cd36f678a09b9a',
        # 'https://weibo.com/p/100808d2399eff31ae7fa46d3ad0c6a751459c',
        # 'https://weibo.com/p/10080804527c4b6d13e391ab855ba4e318c9b1',
    ]
    base_url = "https://www.weibo.com"
    post_num = follower_num = comment_num = 0

    def start_requests(self):
        print("登录中...")
        self.login(username, password)
        time.sleep(3)
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse_topic_info)
        # driver.close()

    def login(self, username, password):
        driver.get("https://login.sina.com.cn/signup/signin.php")
        time.sleep(5)
        driver.save_screenshot("tmp.png")
        if driver.current_url == "https://login.sina.com.cn/signup/signin.php":
            driver.find_element_by_name("username").send_keys(username)
            driver.find_element_by_name("password").send_keys(password)
            driver.save_screenshot("tmp.png")
            driver.find_elements_by_css_selector("input[type='submit']")[0].click()
            time.sleep(8)
            driver.save_screenshot("tmp.png")

            print("\n\n", driver.current_url, "\n\n")

            if driver.current_url != "http://my.sina.com.cn/":
                return False
            else:
                return True
        else:
            return False

    def parse_topic_info(self, response):
        soup = BeautifulSoup(response.body)
        tmp_topic = WeiboTopicItem()
        topic_header = soup.find('div', {"class": "pf_username clearfix"})
        topic_num = soup.find('div', {"class": "PCD_counter"})
        topic_host = soup.find('ul', {"class": "picitems_ul clearfix"})

        title_element = topic_header.find('h1')
        num_list = topic_num.find_all('td', limit=3)
        host_id = topic_host.find('li', {"class": "picitems S_line2"})
        host_name = topic_host.find('a', {"class": "S_txt1"})

        tmp_topic['name'] = title_element.text
        tmp_topic['read_num'] = num_list[0].find('strong').text
        tmp_topic['discuss_num'] = num_list[1].find('strong').text
        tmp_topic['follower_num'] = num_list[2].find('strong').text
        tmp_topic['host_id'] = host_id['uid']
        tmp_topic['host_name'] = host_name.text

        print("获取微博话题信息")
        print("----------------------------------------------------")
        yield tmp_topic

        follower_url = response.url + '/followlist'
        yield Request(url=follower_url, callback=self.parse_follower)

    def parse_follower(self, response):
        print("正在爬取", response.url)
        driver.get(response.url)
        # print(driver.page_source)
        time.sleep(5)
        driver.save_screenshot("tmp.png")

        print("\n爬取粉丝列表")
        print("---------------------\n")

        for follower_item in driver.find_elements_by_xpath('//div[@id="Pl_Core_F4RightUserList__39"]'):
            follower_num = self.MAX_CRAWL_FOLLOWERS
            follower_page_num = self.MAX_CRAWL_FOLLOWERS // 10
            current_follower_num = 0
            current_follower_page_num = 0
            while current_follower_num < follower_num:
                follower_list = follower_item.find_elements_by_xpath('.//ul[@class="follow_list"]/li[@class="follow_item S_line2"]')
                for follower in follower_list:
                    # print(follower)
                    if current_follower_num >= follower_num:
                        break
                    current_follower_num += 1
                    follower_name = follower.find_element_by_xpath(
                        './/div[@class="info_name W_fb W_f14"]//a[1]').get_attribute("title")
                    id = follower.find_element_by_xpath(
                        './/div[@class="info_name W_fb W_f14"]//a[1]').get_attribute("usercard")
                    follower_id = re.sub('\D', '', id.rstrip('&refer_flag=100808'))
                    follower_url = follower.find_element_by_xpath(
                        './/div[@class="info_name W_fb W_f14"]//a[1]').get_attribute('href')
                    print('\n获取粉丝信息[', current_follower_num, ']')
                    print("---------------------\n")
                    followeritem = WeiboTopicFollowerItem(
                        id=follower_id, name=follower_name, url=follower_url
                    )
                    yield followeritem
                if current_follower_page_num < follower_page_num:
                    current_follower_page_num += 1
                    next_button = follower_item.find_element_by_xpath(
                        './/a[@class="page next S_txt1 S_line1"]')
                    js = "window.scrollTo(0,document.body.scrollHeight)"
                    driver.execute_script(js)
                    next_button.click()
                    time.sleep(3)
                print('\n现在的粉丝数量：', current_follower_num, '\n')
        origin_url = response.url.rstrip('/followlist')
        post_url = origin_url + '/emceercd?from=page_huati_rcd_more'
        yield Request(url=post_url, callback=self.parse_post)

    def parse_post(self, response):
        print("正在爬取", response.url)
        driver.get(response.url)
        time.sleep(5)
        driver.save_screenshot("tmp.png")

        print("\n获取微博发布列表")
        print("----------------------\n")

        # for post_item in driver.find_elements_by_xpath('//div[@node-type="feed_list"]'):
        post_num = self.MAX_CRAWL_POSTS
        post_page_num = self.MAX_CRAWL_POSTS // 16
        current_post_num = 0
        current_post_page_num = 0
        while current_post_num < post_num:
            js = "window.scrollTo(0,document.body.scrollHeight)"
            for i in range(0, 2):
                driver.execute_script(js)
                time.sleep(10)
                driver.save_screenshot("tmp.png")
            post_list = driver.find_elements_by_xpath('//div[@action-type="feed_list_item"]')
            for post in post_list:
                if current_post_num >= post_num:
                    break
                current_post_num += 1
                # xpath定位微博发布信息
                publish_name = post.find_element_by_xpath('.//div[@class="WB_info"]//a[1]').get_attribute('title')
                # publish_id = post.get_attribute('tbinfo')
                publish_id = re.sub('\D', '', post.get_attribute('tbinfo'))
                publish_url = post.find_element_by_xpath('.//div[@class="WB_from S_txt2"]//a[1]').get_attribute(
                    'href')
                publish_time = post.find_element_by_xpath('.//div[@class="WB_from S_txt2"]//a[1]').get_attribute(
                    'title')
                # 爬取微博来自，如果没有来自，抛出Post from nowhere异常
                try:
                    pub_from = post.find_element_by_xpath('.//div[@class="WB_from S_txt2"]//a[2]')
                except:
                    publish_from = "Exception[1]:Post from nowhere!"
                else:
                    publish_from = pub_from.text

                forward_num = post.find_element_by_xpath(
                    './/ul[@class="WB_row_line WB_row_r4 clearfix S_line2"]//span[@node-type="forward_btn_text"]//em[2]').text
                comment_num = post.find_element_by_xpath(
                    './/ul[@class="WB_row_line WB_row_r4 clearfix S_line2"]//span[@node-type="comment_btn_text"]//em[2]').text
                like_num = post.find_element_by_xpath(
                    './/ul[@class="WB_row_line WB_row_r4 clearfix S_line2"]//span[@node-type="like_status"]//em[2]').text

                print("\n获取微博发布消息[" + str(current_post_num) + "]")
                print("----------------------")
                # 爬取微博转发，如果没有转发，抛出No Forward异常
                origin_post_name = ""
                origin_post_id = ""
                origin_publish_time = ""
                origin_from = ""
                origin_forward_num = ""
                origin_comment_num = ""
                origin_like_num = ""
                isforward = post.find_elements_by_xpath('.//div[@node-type="feed_list_forwardContent"]')
                for origin_post_item in isforward:
                    try:
                        origin_post_name = origin_post_item.find_element_by_xpath(
                            './/a[@node-type="feed_list_originNick"]').get_attribute('title')
                        id = origin_post_item.find_element_by_xpath(
                            './/a[@node-type="feed_list_originNick"]').get_attribute('usercard')
                        origin_post_id = re.sub('\D', '', id.rstrip('&refer_flag=1008085010_'))
                        origin_publish_time = origin_post_item.find_element_by_xpath(
                            './/a[@node-type="feed_list_item_date"]').get_attribute('title')
                        origin_from = origin_post_item.find_element_by_xpath(
                            './/a[@action-type="app_source"]').text
                        origin_forward_num = origin_post_item.find_element_by_xpath(
                            './/ul[@class="clearfix"]//li[1]//a[1]').text
                        origin_comment_num = origin_post_item.find_element_by_xpath(
                            './/ul[@class="clearfix"]//li[2]').text
                        origin_like_num = origin_post_item.find_element_by_xpath(
                            './/ul[@class="clearfix"]//li[3]//em').text
                    except:
                        print("Exception[2]:No Forward！")
                postitem = WeiboTopicPostItem(
                    url=publish_url, publish_name=publish_name, publish_id=publish_id,
                    publish_time=publish_time, publish_from=publish_from, comment_num=comment_num,
                    forward_num=forward_num, like_num=like_num, origin_post_id=origin_post_id,
                    origin_post_name=origin_post_name, origin_publish_time=origin_publish_time,
                    origin_from=origin_from, origin_comment_num=origin_comment_num, origin_forward_num=origin_forward_num,
                    origin_like_num=origin_like_num
                )
                yield postitem
            if current_post_page_num < post_page_num:
                current_post_page_num += 1
                next_page_url = response.url + '/emceercd?current_page=3&since_id=44&page=' + str(
                    current_post_page_num + 1) + '#Pl_Third_App__46'
                driver.get(next_page_url)
                time.sleep(10)
                # 翻页爬取主持人推荐的微博，如果没有主持人推荐，抛出No more host recommendations异常
                try:
                    host_rec = driver.find_element_by_xpath('//*[@id="Pl_Third_App__46"]/div/div/div[2]/div/ul/li[2]/div/span[1]')
                except:
                    post_num = current_post_num
                    print("Exception[3]:No more host recommendations！")
            print('\n现在的微博发布数量：', current_post_num, '\n')

        yield from self.parse_comment(response.url)

    #爬取一个post页面的comment
    def parse_comment(self, url):
        print("正在爬取", url)
        driver.get(url)
        time.sleep(5)
        driver.find_element_by_xpath('//ul[@class="WB_row_line WB_row_r4 clearfix S_line2"]//a[@action-type="fl_comment"]').click()
        time.sleep(5)
        # driver.save_screenshot("tmp.png")
        filter_time = driver.find_element_by_xpath('//a[@node-type="feed_list_commentTabAll"]')
        filter_time.click()
        time.sleep(5)
        # driver.save_screenshot("tmp.png")
        more_comment = driver.find_element_by_xpath('//a[@class="WB_cardmore S_txt1 S_line1 clearfix"]').get_attribute('href')
        driver.get(more_comment)
        time.sleep(20)
        driver.save_screenshot("tmp.png")

        print("\n爬取评论列表")
        print("-----------------------------\n")
        for comment_item in driver.find_elements_by_xpath('//div[@action-type="feed_list_item"]'):
            comment_button = comment_item.find_element_by_xpath('.//a[@action-type="fl_comment"]')
            comment_num = int(re.findall("\d+", comment_button.text)[0])
            comment_page_num = (comment_num-1) // 49
            current_comment_num = 0
            current_comment_page_num = 0
            comment_num = min(comment_num, self.MAX_CRAWL_COMMENTS)
            while current_comment_num < comment_num:
                js = "window.scrollTo(0,document.body.scrollHeight)"
                for i in range(0, 300):
                    driver.execute_script(js)
                for repeat in driver.find_elements_by_xpath(
                        '//div[@node-type="comment_list"]//div[@class="list_li S_line1 clearfix"]'):
                    if current_comment_num >= comment_num:
                        break
                    current_comment_num += 1
                    id = repeat.get_attribute("comment_id")
                    comment_id = re.sub('\D', '', id)
                    author = repeat.find_element_by_xpath('.//div[@class="WB_text"]//a[1]').text
                    comment_time = repeat.find_element_by_xpath('.//div[@class="WB_func clearfix"]//div[2]').text
                    content = repeat.find_element_by_xpath('.//div[@class="WB_text"]').text
                    print('获取评论消息[' + str(current_comment_num) + ']')
                    print("----------------------------------\n")
                    # print(comment_id)
                    # print(author)
                    # print(comment_time)
                    # print(content)
                    commentitem = WeiboTopicCommentItem(
                        comment_id=comment_id, author=author, comment_time=comment_time, content=content
                    )
                    yield commentitem
                if current_comment_page_num < comment_page_num:
                    current_comment_page_num += 1
                    next_button = comment_item.find_element_by_xpath('.//a[@action-type="click_more_comment"]')
                    next_button.click()
                    time.sleep(0.5)
                    driver.save_screenshot("tmp.png")
            print('\n现在的评论数量：',current_comment_num, '\n')

