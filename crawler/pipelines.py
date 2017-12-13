# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

from crawler import settings
from crawler.items import *


class ZhihuPipeline(object):

    def __init__(self):
        self.connect = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            db=settings.MYSQL_DBNAME,
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASS,
            charset='utf8',
        )
        self.cursor = self.connect.cursor()

    def process_item(self, item, spider):
        if item.__class__ == UserItem:
            try:
                self.cursor.execute("select * from users WHERE name=%s", item['name'])
                ret = self.cursor.fetchone()
                if ret:
                    self.cursor.execute(
                        """update users set name=%s, signature=%s, settlement=%s, industry=%s, work_experience=%s,
                            education_experience=%s, personal_profile=%s, answer_num=%s, question_num=%s, post_num=%s, 
                            post_num=%s, column_num=%s, thinking_num=%s, following_num=%s, follower_num=%s""",
                        (item['name'],
                         item['signature'],
                         item['settlement'],
                         item['industry'],
                         item['work_experience'],
                         item['education_experience'],
                         item['personal_profile'],
                         item['answer_num'],
                         item['question_num'],
                         item['post_num'],
                         item['column_num'],
                         item['thinking_num'],
                         item['following_num'],
                         item['follower_num'],)
                    )
                else:
                    self.cursor.execute(
                        """insert into users(name, signature, settlement, industry, work_experience, 
                            education_experience, personal_profile, answer_num, question_num, post_num, 
                            column_num, thinking_num, following_num, follower_num)
                            values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (item['name'],
                         item['signature'],
                         item['settlement'],
                         item['industry'],
                         item['work_experience'],
                         item['education_experience'],
                         item['personal_profile'],
                         item['answer_num'],
                         item['question_num'],
                         item['post_num'],
                         item['column_num'],
                         item['thinking_num'],
                         item['following_num'],
                         item['follower_num'],)
                    )
                self.connect.commit()
            except Exception as error:
                print(error)
            return item
