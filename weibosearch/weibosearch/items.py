# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WeiboItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    table_name='weibo'

    id=scrapy.Field()
    url=scrapy.Field()
    content=scrapy.Field()
    comment_count=scrapy.Field()
    forword_count=scrapy.Field()
    like_count=scrapy.Field()
    posted_at=scrapy.Field()
    user=scrapy.Field()
    # 爬取时间(如果没有定义会抛出异常被捕获)
    # crawled_at=scrapy.Field()
    keyword=scrapy.Field()