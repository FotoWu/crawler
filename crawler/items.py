# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class UserItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    signature = scrapy.Field()
    settlement = scrapy.Field()
    industry = scrapy.Field()
    work_experience = scrapy.Field()
    education_experience = scrapy.Field()
    personal_profile = scrapy.Field()
    answer_num = scrapy.Field()
    question_num = scrapy.Field()
    post_num = scrapy.Field()
    column_num = scrapy.Field()
    thinking_num = scrapy.Field()
    following_num = scrapy.Field()
    follower_num = scrapy.Field()
    pass


class FollowingListItem(scrapy.Item):
    user_name = scrapy.Field()
    follow_name = scrapy.Field()


class AnswerItem(scrapy.Item):
    title = scrapy.Field()
    title_href = scrapy.Field()
    content = scrapy.Field()
    up_num = scrapy.Field()
    comment_num = scrapy.Field()


class PostItem(scrapy.Item):
    title = scrapy.Field()
    title_href = scrapy.Field()
    content = scrapy.Field()
    up_num = scrapy.Field()
    comment_num = scrapy.Field()


class PostCommentItem(scrapy.Item):
    post_title = scrapy.Field()
    comment_text = scrapy.Field()