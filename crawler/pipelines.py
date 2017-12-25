# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

from crawler import settings
from crawler.items import *
import re


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
        for field in item.fields:
            if 'num' in field:
                item[field] = re.sub(r'\D+', '', item[field])
            item.setdefault(field, "")
        if item.__class__ == UserItem:
            try:
                self.cursor.execute("select * from users WHERE name=%s", item['name'])
                ret = self.cursor.fetchone()
                if ret:
                    self.cursor.execute(
                        """update users set name=%s, signature=%s, settlement=%s, industry=%s, work_experience=%s,
                            education_experience=%s, personal_profile=%s, answer_num=%s, question_num=%s, post_num=%s,
                            post_num=%s, column_num=%s, thinking_num=%s, following_num=%s, follower_num=%s""",
                        (item['name'], item['signature'], item['settlement'], item['industry'], item['work_experience'],
                         item['education_experience'], item['personal_profile'], item['answer_num'], item['question_num'],
                         item['post_num'], item['column_num'], item['thinking_num'], item['following_num'],
                         item['follower_num'],)
                    )
                else:
                    self.cursor.execute(
                        """insert into users(name, signature, settlement, industry, work_experience,
                            education_experience, personal_profile, answer_num, question_num, post_num,
                            column_num, thinking_num, following_num, follower_num)
                            values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (item['name'], item['signature'], item['settlement'], item['industry'], item['work_experience'],
                         item['education_experience'], item['personal_profile'], item['answer_num'], item['question_num'],
                         item['post_num'], item['column_num'], item['thinking_num'], item['following_num'],
                         item['follower_num'],)
                    )
                self.connect.commit()
            except Exception as error:
                print(error)
            return item
        elif item.__class__ == FollowingListItem:
            try:
                self.cursor.execute("select * from following_list where user_name = %s and follow_name = %s",
                                    (item['user_name'], item['follow_name']))
                ret = self.cursor.fetchone()
                if ret is None:
                    self.cursor.execute(
                        "insert into following_list(user_name, follow_name) VALUES (%s, %s)",
                        (item['user_name'], item['follow_name'])
                    )
                self.connect.commit()
            except Exception as error:
                print(error)
                return item
        elif item.__class__ == AnswerItem:
            try:
                self.cursor.execute("select * from answers WHERE title = %s AND content = %s",
                                    (item['title'], item['content']))
                ret = self.cursor.fetchone()
                if ret is None:
                    self.cursor.execute(
                        "insert into answers(title, title_href, content, up_num, comment_num) VALUES(%s,%s,%s,%s,%s)",
                        (item['title'], item['title_href'], item['content'], item['up_num'], item['comment_num'])
                    )
                self.connect.commit()
            except Exception as error:
                print(error)
                return item
        elif item.__class__ == PostItem:
            try:
                self.cursor.execute("select * from posts WHERE title = %s AND title_href=%s",
                                    (item['title'], item['title_href']))
                ret = self.cursor.fetchone()
                if ret is None:
                    self.cursor.execute(
                        "insert into posts(title, title_href, content, up_num, comment_num) VALUES(%s,%s,%s,%s,%s)",
                        (item['title'], item['title_href'], item['content'], item['up_num'], item['comment_num'])
                    )
                self.connect.commit()
            except Exception as error:
                print(error)
                return item
        elif item.__class__ == PostCommentItem:
            try:
                self.cursor.execute("select * from post_comment WHERE post_title=%s AND comment_text=%s",
                                    (item['post_title'], item['comment_text']))
                ret = self.cursor.fetchone()
                if ret is None:
                    self.cursor.execute(
                        "insert into post_comment(post_title, comment_text) VALUES (%s, %s)",
                        (item['post_title'], item['comment_text'])
                    )
                self.connect.commit()
            except Exception as error:
                print(error)
                return item

