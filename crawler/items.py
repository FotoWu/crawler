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


class ZhihuQuestionCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    link = scrapy.Field()
    desc = scrapy.Field()
    pass


class ZhihuQuestionQuestionItem(scrapy.Item):
    id = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()
    comment_count = scrapy.Field()
    answer_count = scrapy.Field()
    pass


class ZhihuQuestionAnswerItem(scrapy.Item):
    id = scrapy.Field()
    question_id = scrapy.Field()
    author = scrapy.Field()
    url = scrapy.Field()
    abstract = scrapy.Field()
    agree_count = scrapy.Field()
    comment_count = scrapy.Field()
    pass


class ZhihuQuestionCommentItem(scrapy.Item):
    related_id = scrapy.Field()
    author = scrapy.Field()
    release_time = scrapy.Field()
    content = scrapy.Field()
    pass


class WeiboTopicItem(scrapy.Item):
    #id = scrapy.Field()
    name = scrapy.Field()
    read_num = scrapy.Field()
    discuss_num = scrapy.Field()
    follower_num = scrapy.Field()
    host_name = scrapy.Field()
    host_id = scrapy.Field()
    pass


class WeiboTopicPostItem(scrapy.Item):
    url = scrapy.Field()
    publish_name = scrapy.Field()
    publish_id = scrapy.Field()
    publish_time = scrapy.Field()
    publish_from = scrapy.Field()
    comment_num = scrapy.Field()
    forward_num = scrapy.Field()
    like_num = scrapy.Field()
    origin_post_id = scrapy.Field()
    origin_post_name = scrapy.Field()
    origin_publish_time = scrapy.Field()
    origin_from = scrapy.Field()
    origin_comment_num = scrapy.Field()
    origin_forward_num = scrapy.Field()
    origin_like_num = scrapy.Field()
    pass


class WeiboTopicCommentItem(scrapy.Item):
    comment_id = scrapy.Field()
    author = scrapy.Field()
    comment_time = scrapy.Field()
    content = scrapy.Field()
    pass


class WeiboTopicFollowerItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    pass


class WeibosearchItem(scrapy.Item):
        link = scrapy.Field()  # link
        pub_name = scrapy.Field()  # 发布人
        pub_id = scrapy.Field()  # 发布人id
        time = scrapy.Field()  # 发布时间（转化为绝对时间）
        where = scrapy.Field()  # 来自
        comment_number = scrapy.Field()  # 评论数
        comment_list = scrapy.Field()  # 评论列表（前50）
        like_number = scrapy.Field()  # 赞数
        transmit_number = scrapy.Field()  # 转发数
        forward_flag = scrapy.Field()  # 本post是否转发
        pre_pub_id = scrapy.Field()  # 原post发布人，
        pre_time = scrapy.Field()  # 原post发布时间（转化为绝对时间）
        pre_where = scrapy.Field()  # 原post来自
        pre_comment_number = scrapy.Field()  # 原post评论数
        pre_like_number = scrapy.Field()  # 原post赞数
        pre_transmit_number = scrapy.Field()  # 原post转发数
        pass

class SearchContentItem(scrapy.Item):
    id = scrapy.Field()
    keyword =  scrapy.Field()
    title = scrapy.Field()
    title_href = scrapy.Field()
    author = scrapy.Field()
    vote_num = scrapy.Field()
    comment_num = scrapy.Field()
    pass


class SearchContentCommentItem(scrapy.Item):
    id = scrapy.Field()
    keyword = scrapy.Field()
    author = scrapy.Field()
    content = scrapy.Field()
    pass


class SearchUserItem(scrapy.Item):
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


class SearchFollowingListItem(scrapy.Item):
    user_name = scrapy.Field()
    follow_name = scrapy.Field()
    pass


class SearchTopicItem(scrapy.Item):
    id = scrapy.Field()
    keyword =  scrapy.Field()
    title = scrapy.Field()
    title_href = scrapy.Field()
    content = scrapy.Field()
    follow_num = scrapy.Field()
    question_num = scrapy.Field()
    essence_num = scrapy.Field()
    pass
