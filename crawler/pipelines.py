# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

from crawler import settings
from crawler.items import *
import re


class ZhihuIdPipeline(object):

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
        else:
            return item


class ZhihuQuestionPipeline(object):
    def open_spider(self, spider):
        pass

    def __init__(self):
        self.connect = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            db='zhihu_questions',
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASS,
            charset='utf8',
        )
        self.cursor = self.connect.cursor()

    def process_item(self, item, spider):
        if item.__class__ == ZhihuQuestionQuestionItem:
            for each in item:
                item[each] = item[each].replace("'", "\\\'")
            try:
                self.cursor.execute("select * from question WHERE id = %s",
                                    (item['id']))
                ret = self.cursor.fetchone()
                if ret is None:
                    sql = "use zhihu_questions; insert into question values(" + item['id'] + ",'" + item[
                        'url'] + "','" + item['name'] + "','" + item['comment_count'] + "','" + item[
                              'answer_count'] + "')".encode('utf-8').decode('utf-8')
                    self.cursor.execute(sql)
                self.connect.commit()
            except Exception as error:
                print(error)
                return item
        if item.__class__ == ZhihuQuestionCommentItem:
            for each in item:
                item[each] = item[each].replace("'", "\\\'")
            try:
                self.cursor.execute("select * from comment WHERE related_id = %s and author = %s",
                                    (item['related_id'],item['author']))
                ret = self.cursor.fetchone()
                if ret is None:
                    item['content'].replace("'", "\'")
                    sql = "use zhihu_questions; insert into comment values(" + item['related_id'] + ",'" + item[
                        'author'] + "','" + item['release_time'] + "','" + item['content'] + "')".encode(
                        'utf-8').decode('utf-8')
                    self.cursor.execute(sql)
                self.connect.commit()
            except Exception as error:
                print(error)
                return item
        if item.__class__ == ZhihuQuestionAnswerItem:
            for each in item:
                item[each] = item[each].replace("'", "\\\'")
            try:
                self.cursor.execute("select * from answer WHERE id = %s",
                                    (item['id']))
                ret = self.cursor.fetchone()
                if ret is None:
                    sql = "use zhihu_questions; insert into answer values(" + item['id'] + "," + item[
                        'question_id'] + ",'" + item['author'] + "','" + item['url'] + "','" + item[
                              'abstract'] + "','" + item['agree_count'] + "','" + item['comment_count'] + "')".encode(
                        'utf-8').decode('utf-8')
                    self.cursor.execute(sql)
                self.connect.commit()
            except Exception as error:
                print(error)
                return item
        return item


class SearchCrawlerPipeline(object):
    def __init__(self):
        self.connect = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            db='zhihuSearch',
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
        if item.__class__ == SearchContentItem:
            try:
                self.cursor.execute("select * from search_content WHERE title=%s", item['title'])
                ret = self.cursor.fetchone()
                if ret:
                    self.cursor.execute(
                        """update search_content set id=%s, keyword=%s, title=%s, title_href=%s, author=%s, vote_num=%s, comment_num=%s
                        WHERE title=%s
                     """,
                        (item['id'], item['keyword'], item['title'], item['title_href'], item['author'],
                         item['vote_num'], item['comment_num'], item['title'],)
                    )
                else:
                    self.cursor.execute(
                        """insert into search_content(id, keyword, title, title_href, author, vote_num, comment_num)
                            values(%s, %s, %s, %s, %s, %s, %s)""",
                        (item['id'], item['keyword'], item['title'], item['title_href'], item['author'],
                         item['vote_num'], item['comment_num'],)
                    )
                self.connect.commit()
            except Exception as error:
                print(error)
            return item
        elif item.__class__ == SearchContentCommentItem:
            try:
                self.cursor.execute(
                    "select * from search_content_comment WHERE id=%s and author=%s and content=%s",
                    (item['id'], item['author'], item['content']),
                )
                ret = self.cursor.fetchone()
                if ret is None:
                    self.cursor.execute(
                        """insert into search_content_comment(id, keyword, author, content) values(%s, %s, %s, %s)""",
                        (item['id'], item['keyword'], item['author'], item['content'],)
                    )
                self.connect.commit()
            except Exception as error:
                print(error)
            return item
        elif item.__class__ == SearchUserItem:
            try:
                self.cursor.execute("select * from search_users WHERE name=%s", item['name'])
                ret = self.cursor.fetchone()
                if ret:
                    self.cursor.execute(
                        """update search_users set name=%s, signature=%s, settlement=%s, industry=%s, work_experience=%s,
                          education_experience=%s, personal_profile=%s, answer_num=%s, question_num=%s,
                          post_num=%s, column_num=%s, thinking_num=%s, follower_num=%s WHERE name=%s""",
                        (item['name'], item['signature'], item['settlement'], item['industry'], item['work_experience'],
                         item['education_experience'], item['personal_profile'], item['answer_num'],
                         item['question_num'],
                         item['post_num'], item['column_num'], item['thinking_num'], item['following_num'],
                         item['name'])
                    )
                else:
                    self.cursor.execute(
                        """insert into search_users(name, signature, settlement, industry, work_experience,
                            education_experience, personal_profile, answer_num, question_num, post_num,
                            column_num, thinking_num, following_num, follower_num)
                            values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (item['name'], item['signature'], item['settlement'], item['industry'], item['work_experience'],
                         item['education_experience'], item['personal_profile'], item['answer_num'],
                         item['question_num'],
                         item['post_num'], item['column_num'], item['thinking_num'], item['following_num'],
                         item['follower_num'],)
                    )
                self.connect.commit()
            except Exception as error:
                print(error)
            return item
        elif item.__class__ == SearchFollowingListItem:
            try:
                self.cursor.execute("select * from search_following_list where user_name = %s and follow_name = %s",
                                    (item['user_name'], item['follow_name']))
                ret = self.cursor.fetchone()
                if ret is None:
                    self.cursor.execute(
                        "insert into search_following_list(user_name, follow_name) VALUES (%s, %s)",
                        (item['user_name'], item['follow_name'])
                    )
                self.connect.commit()
            except Exception as error:
                print(error)
                return item
        elif item.__class__ == SearchTopicItem:
            try:
                self.cursor.execute("select * from search_topic WHERE title=%s", item['title'])
                ret = self.cursor.fetchone()
                if ret:
                    self.cursor.execute(
                        """update search_topic set id=%s, keyword=%s, title=%s, title_href=%s, content=%s, 
                        follow_num=%s, question_num=%s, essence_num=%s WHERE title=%s
                     """,
                        (item['id'], item['keyword'], item['title'], item['title_href'], item['content'],
                         item['follow_num'], item['question_num'], item['essence_num'], item['title'],
                         )
                    )
                else:
                    self.cursor.execute(
                        """insert into search_topic(id, keyword, title, title_href, content, follow_num, 
                        question_num, essence_num)
                            values(%s, %s, %s, %s, %s, %s, %s, %s)""",
                        (item['id'], item['keyword'], item['title'], item['title_href'], item['content'],
                         item['follow_num'], item['question_num'], item['essence_num'],)
                    )
                self.connect.commit()
            except Exception as error:
                print(error)
            return item