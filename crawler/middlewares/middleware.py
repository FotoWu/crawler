from selenium import webdriver
from scrapy.http import HtmlResponse
import time


class JavaScriptMiddleware(object):
    def process_request(self, request, spider):
        if 'zhihu' or 'weibo' in spider.name:
            print("PhantomJs is starting...")
            driver = webdriver.PhantomJS(executable_path='/home/ubuntu/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
            driver.get(request.url)
            time.sleep(2)
            if spider.name == 'zhihuId':
                show_more_button = driver.find_element_by_xpath("//button[@class='Button ProfileHeader-expandButton Button--plain']")
                show_more_button.click()
            body = driver.page_source
            print("访问", request.url)
            return HtmlResponse(request.url, body=body, encoding='utf-8', request=request)
        else:
            return
