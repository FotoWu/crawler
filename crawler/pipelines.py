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
            db="zhihu",
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
            db="zhihu_questions",
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


class WeiboTopicPipeline(object):

    def __init__(self):
        self.connect = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            db="weibo",
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASS,
            charset='utf8',
        )
        self.cursor = self.connect.cursor()

    def process_item(self, item, spider):
        for field in item.fields:
            # if 'num' in field:
            #     item[field] = re.sub(r'\D+', '', item[field])
            item.setdefault(field, "")
        if item.__class__ == WeiboTopicItem:
            try:
                self.cursor.execute("select * from topic WHERE name=%s", item['name'])
                ret = self.cursor.fetchone()
                if ret:
                    self.cursor.execute(
                        """update topic set name=%s, read_num=%s, discuss_num=%s, follower_num=%s,
                        host_name=%s, host_id=%s""",
                        (item['name'], item['read_num'], item['discuss_num'], item['follower_num'],
                         item['host_name'], item['host_id'],)
                    )
                else:
                    self.cursor.execute(
                        """insert into topic(name, read_num, discuss_num, follower_num, host_name, host_id)
                          values(%s, %s, %s, %s, %s, %s)""",
                        (item['name'], item['read_num'], item['discuss_num'], item['follower_num'],
                         item['host_name'], item['host_id'],)
                    )
                self.connect.commit();
            except Exception as error:
                print(error)
            return item
        elif item.__class__ == WeiboTopicFollowerItem:
            try:
                self.cursor.execute("select * from follower WHERE id=%s", item['id'])
                ret = self.cursor.fetchone()
                if ret:
                    self.cursor.execute(
                        """update follower set id=%s, name=%s, url=%s""",
                        (item['id'], item['name'], item['url'],)
                    )
                else:
                    self.cursor.execute(
                        """insert into follower(id, name, url)
                          values(%s, %s, %s)""",
                        (item['id'], item['name'], item['url'],)
                    )
                self.connect.commit();
            except Exception as error:
                print(error)
            return item
        elif item.__class__ == WeiboTopicPostItem:
            try:
                self.cursor.execute("select * from post WHERE url=%s", item['url'])
                ret = self.cursor.fetchone()
                if ret:
                    self.cursor.execute(
                        """update post set url=%s, publish_name=%s, publish_id=%s, publish_time=%s,
                        publish_from=%s, forward_num=%s, comment_num=%s, like_num=%s, origin_post_id=%s,
                        origin_post_name=%s, origin_publish_time=%s, origin_from=%s, origin_forward_num=%s,
                        origin_comment_num=%s, origin_like_num=%s""",
                        (item['url'], item['publish_name'], item['publish_id'], item['publish_time'],
                         item['publish_from'], item['forward_num'], item['comment_num'], item['like_num'], item['origin_post_id'],
                            item['origin_post_name'], item['origin_publish_time'], item['origin_from'], item['origin_forward_num'],
                            item['origin_comment_num'], item['origin_like_num'],)
                    )
                else:
                    self.cursor.execute(
                        """insert into post(url, publish_name, publish_id, publish_time, publish_from, forward_num,
                        comment_num, like_num, origin_post_id, origin_post_name, origin_publish_time, origin_from, origin_forward_num,
                        origin_comment_num, origin_like_num)
                          values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (item['url'], item['publish_name'], item['publish_id'], item['publish_time'],
                         item['publish_from'], item['forward_num'], item['comment_num'], item['like_num'],
                         item['origin_post_id'],
                         item['origin_post_name'], item['origin_publish_time'], item['origin_from'],
                         item['origin_forward_num'],
                         item['origin_comment_num'], item['origin_like_num'],)
                    )
                self.connect.commit();
            except Exception as error:
                print(error)
            return item
        elif item.__class__ == WeiboTopicCommentItem:
            try:
                self.cursor.execute("select * from comment WHERE comment_id=%s", item['comment_id'])
                ret = self.cursor.fetchone()
                if ret:
                    self.cursor.execute(
                        """update comment set comment_id=%s, author=%s, comment_time=%s, content=%s""",
                        (item['comment_id'], item['author'], item['comment_time'], item['content'],)
                    )
                else:
                    self.cursor.execute(
                        """insert into comment(comment_id, author, comment_time, content)
                          values(%s, %s, %s, %s)""",
                        (item['comment_id'], item['author'], item['comment_time'], item['content'],)
                    )
                self.connect.commit();
            except Exception as error:
                print(error)
            return item


class WeibosearchPipeline(object):

    def __init__(self):
        self.connect = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            db="weibosearch",
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASS,
            charset='utf8',
        )
        self.cursor = self.connect.cursor()

    def process_item(self, item, spider):
        print("begin1")
        if item.__class__ == WeibosearchItem:
            print("begin2")
            try:
                self.cursor.execute("select * from weibosearch WHERE link=%s",item['link'])
                ret = self.cursor.fetchone()
                if ret:
                    self.cursor.execute(
                        """update weibosearch set link=%s, pub_name=%s,pub_id=%s, pub_time=%s, comefrom=%s, comment_number=%s,
                        comment_list=%s, like_number=%s, transmit_number=%s, forward_flag=%s,pre_pub_id=%s,pre_pub_time=%s,
                        pre_comefrom=%s,pre_comment_number=%s ,pre_like_number=%s,pre_transmit_number=%s""",
                        (item['link'], item['pub_name'], item['pub_id'], item['time'], item['where'],
                         item['comment_number'], item['comment_list'],item['like_number'], item['transmit_number'],
                         item['forward_flag'], item['pre_pub_id'],item['pre_time'],item['pre_where'],item['pre_comment_number'],
                         item['pre_like_number'],item['pre_transmit_number'],)
                    )
                else:
                    print("insert ing")
                    self.cursor.execute(
                        """insert into weibosearch(link, pub_name, pub_time,pub_id, comefrom, comment_number,comment_list, like_number, 
                        transmit_number, forward_flag,pre_pub_id,pre_pub_time,pre_comefrom,pre_comment_number,pre_like_number,pre_transmit_number)
                          values:%s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s,%s,%s""",
                        (item['link'], item['pub_name'], item['pub_id'], item['time'], item['where'],
                         item['comment_number'], item['comment_list'],item['like_number'], item['transmit_number'],
                         item['forward_flag'], item['pre_pub_id'],item['pre_time'],item['pre_where'],item['pre_comment_number'],
                         item['pre_like_number'],item['pre_transmit_number'],)
                    )
                self.connect.commit()
            except Exception as error:
                print(error)
        return item
