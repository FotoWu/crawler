# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from selenium.webdriver.remote.remote_connection import LOGGER
import logging
import time
import re
from selenium import webdriver
from crawler.items import *
from crawler.settings import PhantomJS_PATH

LOGGER.setLevel(logging.WARNING)
username = '15999058069'
password = '19970507llc'
service_args = ['--load-images=no', '--disk-cache=yes', '--ignore-ssl-errors=true']
driver = webdriver.PhantomJS(executable_path=PhantomJS_PATH, service_args=service_args)
message = webdriver.PhantomJS(executable_path=PhantomJS_PATH, service_args=service_args)


class WeibotsearchSpider(scrapy.Spider):

    MAX_CRAWL_FOLLOWERS = 100
    MAX_CRAWL_POSTS = 500
    MAX_CRAWL_COMMENTS = 50

    name = 'weibosearch'
    allowed_domains = ['weibo.com']
    start_urls = [
        "https://s.weibo.com/weibo/校庆&b=1&page=",
        "https://s.weibo.com/weibo/软件工程&b=1&page=",
        "https://s.weibo.com/weibo/章子怡演技&b=1&page=",
        "https://s.weibo.com/weibo/软件测试&b=1&page=",
        "https://s.weibo.com/weibo/微博之夜&b=1&page=",
        "https://s.weibo.com/weibo/支付宝&b=1&page=",
        "https://s.weibo.com/weibo/健康&b=1&page=",
        "https://s.weibo.com/weibo/睡眠&b=1&page=",
        "https://s.weibo.com/weibo/脱发&b=1&page=",
        "https://s.weibo.com/weibo/浙江大学&b=1&page=",
    ]

    def parse(self, response):
        print('##########################')
        print("登录中...")
        self.login(username, password)
        time.sleep(5)
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse_post)

    def login(self, username, password):
        driver.get("https://login.sina.com.cn/signup/signin.php")
        time.sleep(5)
        driver.save_screenshot("tmp1.png")
        if driver.current_url == "https://login.sina.com.cn/signup/signin.php":
            driver.find_element_by_name("username").send_keys(username)
            driver.find_element_by_name("password").send_keys(password)
            driver.save_screenshot("tmp.png")
            driver.find_elements_by_css_selector("input[type='submit']")[0].click()
            time.sleep(8)
            driver.save_screenshot("tmp1.png")

            print("\n\n", driver.current_url, "\n\n")

            if driver.current_url != "http://my.sina.com.cn/":
                return False
            else:
                return True
        else:
            return False

    def parse_post(self, response):
        print("\n\n搜索结果\n\n",response.url)
        for i in range(1,26):
            driver.get(response.url+str(i))
            driver.implicitly_wait(5)
            driver.save_screenshot("tmp2.png")
            print("已保存截图1")

            for post_item in driver.find_elements_by_xpath('//div[@node-type="feed_list"]'):
                post_list = post_item.find_elements_by_xpath('.//div[@class="WB_cardwrap S_bg2 clearfix"]')
                js="window.scrollTo(0,document.body.scrollHeight)"
                for i in range(0,20):
                    driver.execute_script(js)
                j=0
                for post in post_list:
                    j+=1
                    print("\t获取搜索结果信息",j)
                    link = post.find_element_by_xpath('.//div[@class="feed_from W_textb"]//a[1]').get_attribute('href')
                    t = post.find_element_by_xpath('.//div[@class="feed_from W_textb"]//a[1]').get_attribute('title')
                    message.get(link+'&type=comment')
                    #message.get("https://weibo.com/1894287893/FCoyzdngO?refer_flag=1001030103_&type=comment")
                    time.sleep(10)
                    for i in range(0, 20):
                         message.execute_script(js)
                    message.save_screenshot("message.png")
                    pub_name = message.find_element_by_xpath('//div[@class="WB_info"]').text
                    pub_id = message.find_element_by_xpath('//div[@class="WB_info"]//a[1]').get_attribute('usercard')
                    pub_id = re.sub("\D", "", pub_id)
                    pub_id = pub_id[:-1]
                    try:
                        where_test = message.find_element_by_xpath("//a[@action-type='app_source']")
                    except:
                        where = "Post from nowhere."
                    else:
                        where = where_test.text
                    comment_number = message.find_element_by_xpath("//a[@class='S_txt2' and @action-type='fl_comment']//span//span//span//em[2]").text
                    like_number = message.find_element_by_xpath("//a[@class='S_txt2' and @action-type='fl_like']//span//span//span//em[2]").text
                    transmit_number = message.find_element_by_xpath("//a[@class='S_txt2' and @action-type='fl_forward']//span//span//span//em[2]").text
                    comment_list_all = message.find_elements_by_xpath("//div[@node-type='comment_list']//div[@class='list_li S_line1 clearfix']//div[@class='WB_text']")
                    try:
                        pre = message.find_element_by_xpath("//div[@class='WB_feed_expand']")
                    except:
                        pre_flag = 0
                    else:
                        pre_flag = 1
                    if (pre_flag==1):
                        # print(pre)
                        pre_id = pre.find_element_by_xpath("//a[@class='W_fb S_txt1']").get_attribute('title')
                        pre_time = pre.find_element_by_xpath("//a[@node-type='feed_list_item_date']").get_attribute('title')
                        pre_comment_number=message.find_element_by_xpath(".//div[2] //div[5] // div[1] // ul // li[1] // span // a // span // em[2]").text
                        pre_transmit_number=pre.find_element_by_xpath(".//div[@class='WB_handle W_fr']//ul[@class='clearfix']//li[2]//span//a//span//em[2]").text
                        pre_like_number=pre.find_element_by_xpath(".//div[@class='WB_handle W_fr']//ul[@class='clearfix']//li[3]//span//a//span//em[2]").text
                        try:
                            pre_test = pre.find_element_by_xpath("//a[@action-type='app_source']")
                        except:
                            pre_where = "Post from nowhere."
                        else:
                            pre_where = pre_test.text
                        # print(pre_id,pre_time,pre_where,pre_comment_number,pre_like_number,pre_transmit_number)
                    else:
                        pre_id = " "
                        pre_time = " "
                        pre_comment_number=" "
                        pre_transmit_number=" "
                        pre_like_number=" "
                        pre_where = " "
                    # print("link:  ",link)
                    # print("time:  ",t)
                    # print("pub name:  ",pub_name)
                    # print("pub id:  ",pub_id)
                    # print("from:  ",where)
                    # print("comment num:  ",comment_number)
                    # print("like num:  ", like_number)
                    # print("transmit num:  ", transmit_number)
                    comment_list=[]
                    k = 0
                    for comment in comment_list_all:
                        k+=1
                        if (k==50):
                            break
                        comment_list.append(comment.text)
                        # print("comment  :",comment.text)
                    s_list="|".join(comment_list)
                    # print("\n")
                    wsitem=WeibosearchItem(link=link,pub_name=pub_name,pub_id=pub_id,time=time,where=where,comment_number=comment_number,
                                           comment_list=s_list,like_number=like_number,transmit_number=transmit_number,forward_flag=pre_flag,
                                           pre_pub_id=pre_id,pre_time=pre_time,pre_where=pre_where,pre_comment_number=pre_comment_number,
                                           pre_like_number=pre_like_number,pre_transmit_number=pre_transmit_number)
                    yield wsitem


