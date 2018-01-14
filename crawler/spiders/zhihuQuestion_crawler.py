import scrapy
import urllib.request
import time
import re
from selenium import webdriver
from crawler.items import *
from crawler.settings import PhantomJS_PATH
import requests

class ZhihuQuestionSpider(scrapy.Spider):

    MAX_COMMENT_NUM = 30
    MAX_ANSWER_NUM = 500

    # question_sql=questionSql()
    now_question_id=-1

    name = "zhihuQuestion"
    allowed_domains = ["zhihuQuestion.org"]
    start_urls = [
        "https://www.zhihu.com/question/263770409",
        "https://www.zhihu.com/question/50364416",
        "https://www.zhihu.com/question/263508141",
        "https://www.zhihu.com/question/37284137",
        "https://www.zhihu.com/question/66704959",
        "https://www.zhihu.com/question/31102779",
        "https://www.zhihu.com/question/59497935",
        "https://www.zhihu.com/question/21732066",
        "https://www.zhihu.com/question/35236983"
    ]

    def parse(self, response):
        yield from self.parse_question_info (response)
        yield from self.parse_answer_list(response)
        yield from self.parse_comment_list(response)

    def parse_question_info(self,response):
        print ("获取问题信息")
        driver = webdriver.PhantomJS(executable_path=PhantomJS_PATH)
        driver.get(response.url)
        driver.implicitly_wait(5)

        print ("\t获取问题基本信息")
        tmp_question = ZhihuQuestionQuestionItem()
        question_info=response.xpath("//div[@class='QuestionPage']")
        tmp_question['name']=question_info.xpath(".//meta[@itemprop='name']/@content").extract()[0]
        tmp_question['url'] = question_info.xpath(".//meta[@itemprop='url']/@content").extract()[0]
        tmp_question['answer_count'] = question_info.xpath(".//meta[@itemprop='answerCount']/@content").extract()[0]
        tmp_question['comment_count'] = question_info.xpath(".//meta[@itemprop='commentCount']/@content").extract()[0]
        tmp = tmp_question['url'].split('/')
        tmp_question['id'] = tmp[len(tmp)-1]
        self.now_question_id=tmp_question['id']
        yield tmp_question
        # self.question_sql.insertIntoQuestion(tmp_question)
        print ("当前问题ID",tmp_question['id'])
        print ("\t获取问题评论")
        comment_button=driver.find_element_by_xpath(".//div[@class='QuestionHeader-Comment']/button[contains(@class, 'Button--withIcon')]")
        comment_button.click()
        time.sleep(0.5)
        comment_list = driver.find_elements_by_xpath(
            "//div[@class='CommentItem']")

        for comment in comment_list:
            comment_data = ZhihuQuestionCommentItem()
            comment_data['related_id'] = tmp_question['id']
            comment_text = comment.text.split("\n")[0:-1]
            comment_data['author'] = comment_text[0]
            comment_data['content'] = comment_text[1]
            comment_data['release_time'] = ""
            print ("\t\t正在获取",comment_data['author'],"的评论")
            # self.question_sql.insertIntoComment(comment_data)
            yield comment_data





    def parse_answer_list(self,response):
        print ("获取回答信息")
        answer_list = response.xpath(".//div[@class='List-item']")
        for answer in answer_list:
            answer_data=ZhihuQuestionAnswerItem()
            answer_data['id']=answer.xpath(".//div[@class='ContentItem AnswerItem']/@name").extract()[0]
            tmp = response.url.split('/')
            answer_data['question_id']=tmp[len(tmp) - 1]
            answer_data['author']=answer.xpath(".//meta[@itemprop='name']/@content").extract()[0]
            answer_data['url']=answer.xpath(".//meta[@itemprop='url']/@content").extract()[0]
            answer_data['abstract']=answer.xpath(".//div[@class='RichText AuthorInfo-badgeText']/text()").extract()
            answer_data['agree_count']=answer.xpath(".//button[@class='Button VoteButton VoteButton--up']/text()").extract()[0]
            answer_data['comment_count']=answer.xpath(".//button[@class='Button ContentItem-action Button--plain Button--withIcon Button--withLabel']/text()").extract()[0]
            print ("\t正在获取",answer_data['author'],"的回答")
            if len(answer_data['abstract'])<1:
                answer_data['abstract']='null'
            else:
                answer_data['abstract'] = answer_data['abstract'][0]
            answer_data['comment_count']=re.findall("\d+", answer_data['comment_count'])
            if(len(answer_data['comment_count'])>0):
                answer_data['comment_count']=answer_data['comment_count'][0]
            else:
                answer_data['comment_count'] = '0'
            yield answer_data
            # self.question_sql.insertIntoAnswer(answer_data)

            # print (comment_count)


    def parse_comment_list(self,response):
        print ("获取回答评论信息")
        driver = webdriver.PhantomJS(executable_path=PhantomJS_PATH)
        driver.get(response.url)
        driver.implicitly_wait(5)
        js = "window.scrollTo(0,document.body.scrollHeight)"
        for i in range(0, 300):
            driver.execute_script(js)
            # time.sleep(0.5)
        for answer in driver.find_elements_by_xpath("//div[@class='List-item']"):
            question_id = answer.find_element_by_xpath(".//div[@class='ContentItem AnswerItem']").get_attribute("name")

            print ("\t正在获取",question_id,"的评论")
            comment_button=answer.find_element_by_xpath(".//button[contains(@class, 'Button--withIcon')]")
            # print (comment_button.text,'\n')

            # comment_num = int(re.findall("\d+", comment_button.text)[0])
            tmp = re.findall("\d+", comment_button.text)
            if len(tmp)<1:
                comment_num=0
            else:
                comment_num=int(tmp[0])
            comment_page_num = (comment_num - 1) // 20
            # print ("page num", comment_page_num)
            comment_button.click()
            time.sleep(0.5)
            current_comment_num = 0
            current_comment_page_num = 0
            comment_num = min(comment_num, self.MAX_COMMENT_NUM)
            while current_comment_num < comment_num:
                comment_items = answer.find_elements_by_xpath(
                    ".//div[@class='Comments-container']//div[@class='CommentItem']")
                print ("页内数量为",len(comment_items))
                if len(comment_items)==0:
                    break
                for comment_item in comment_items:
                    if current_comment_num >= comment_num:
                        break
                    current_comment_num += 1
                    comment_text = comment_item.text.split("\n")[0:-1]
                    comment_data=ZhihuQuestionCommentItem()
                    comment_data['author']=comment_text[0]
                    comment_data['release_time']=comment_text[1]
                    comment_data['content']=comment_text[2]
                    comment_data['related_id']=question_id
                    yield comment_data
                    # self.question_sql.insertIntoComment(comment_data)

                if current_comment_page_num < comment_page_num:
                    current_comment_page_num += 1
                    try:
                        next_button = answer.find_element_by_xpath(".//button[contains(@class, 'PaginationButton-next')]")
                        next_button.click()
                        time.sleep(0.5)
                    except:
                        continue

