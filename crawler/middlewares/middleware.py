from selenium import webdriver
from scrapy.http import HtmlResponse
import time
from crawler.settings import PhantomJS_PATH


class JavaScriptMiddleware(object):
    def process_request(self, request, spider):
        if 'zhihuId' in spider.name:
            print("PhantomJs is starting...")
            driver = webdriver.PhantomJS(executable_path=PhantomJS_PATH)
            driver.get(request.url)
            time.sleep(0.5)
            if spider.name == 'zhihuId_answer':
                try:
                    show_more_button = driver.find_element_by_xpath("//button[@class='Button ProfileHeader-expandButton Button--plain']")
                    show_more_button.click()
                except Exception:
                    print("没有多余信息")
            body = driver.page_source
            print("访问", request.url)
            return HtmlResponse(request.url, body=body, encoding='utf-8', request=request)
        if 'zhihuQuestion' in spider.name:
            print("PhantomJs is starting...")
            driver = webdriver.PhantomJS(executable_path=PhantomJS_PATH)
            driver.get(request.url)
            driver.implicitly_wait(5)
            js = "window.scrollTo(0,document.body.scrollHeight)"
            for i in range(0,300):
                driver.execute_script(js)
                # time.sleep(0.5)
            print ("已保存截图")
            driver.save_screenshot("tmp.png")
            body = driver.page_source
            print("访问", request.url)
            return HtmlResponse(request.url, body=body, encoding='utf-8', request=request)
        if 'weibotopic' in spider.name:
            print("PhantomJs is starting...")
            service_args = ['--load-images=no', '--disk-cache=yes', '--ignore-ssl-errors=true']
            driver = webdriver.PhantomJS(executable_path=PhantomJS_PATH, service_args=service_args)
            driver.get(request.url)
            time.sleep(5)
            js = "window.scrollTo(0,document.body.scrollHeight)"
            for i in range(0, 300):
                driver.execute_script(js)
                # time.sleep(0.1)
            print("已保存截图")
            driver.save_screenshot("tmp.png")
            body = driver.page_source
            print("访问", request.url)
            # driver.quit()
            return HtmlResponse(request.url, body=body, encoding='utf-8', request=request)
        if 'weibosearch' in spider.name:
            print("PhantomJs is starting...")
            service_args = ['--load-images=no', '--disk-cache=yes', '--ignore-ssl-errors=true']
            driver = webdriver.PhantomJS(executable_path=PhantomJS_PATH, service_args=service_args)
            # driver.implicitly_wait(5)
            time.sleep(5)
            js = "window.scrollTo(0,document.body.scrollHeight)"
            for i in range(0, 300):
                driver.execute_script(js)
                # time.sleep(0.5)
            print("已保存截图")
            driver.save_screenshot("tmp.png")
            body = driver.page_source
            print("访问", request.url)
            return HtmlResponse(request.url, body=body, encoding='utf-8', request=request)
        if 'zhihuSearch' in spider.name:
            driver = webdriver.PhantomJS(executable_path=PhantomJS_PATH)
            driver.get(request.url)
            time.sleep(0.5)
            if spider.name == 'zhihuSearchUser':
                try:
                    show_more_button = driver.find_element_by_xpath("//button[@class='Button ProfileHeader-expandButton Button--plain']")
                    show_more_button.click()
                except Exception:
                    print("暂无更多资料")
            body = driver.page_source
            driver.close()
            driver.quit()
            return HtmlResponse(request.url, body=body, encoding='utf-8', request=request)
        else:
            return
