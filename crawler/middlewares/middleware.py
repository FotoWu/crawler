from selenium import webdriver
from scrapy.http import HtmlResponse
import time


class JavaScriptMiddleware(object):
    def process_request(self, request, spider):
        if 'zhihu' or 'weibo' in spider.name:
            print("PhantomJs is starting...")
            driver = webdriver.PhantomJS(executable_path='/Users/linsp/Downloads/phantomjs-2.1-2.1-macosx/bin/phantomjs')
            driver.get(request.url)
            if 'weibo' in spider.name:
                time.sleep(3)
            else:
                time.sleep(0.5)
            if spider.name == 'zhihuId':
                try:
                    show_more_button = driver.find_element_by_xpath("//button[@class='Button ProfileHeader-expandButton Button--plain']")
                    show_more_button.click()
                except Exception:
                    print("没有多余信息")
            body = driver.page_source
            print("访问", request.url)
            return HtmlResponse(request.url, body=body, encoding='utf-8', request=request)
        else:
            return
