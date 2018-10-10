# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import time

import pymongo

from .items import WeiboItem
import re

class WeiboPipeline(object):
    def process_item(self, item, spider):
        #处理时间格式
        if isinstance(item,WeiboItem):
            if item.get('content'):
                item['content']=item['content'].lstrip(":").strip()
            if item.get('posted_at'):
                item['posted_at']=item['posted_at'].strip()
                item['posted_at']=self.parse_time(item['posted_at'])
        return item

    def parse_time(self,datetime):
        if re.match('\d+月\d+日',datetime):
            datetime=time.strftime('%Y{}',time.localtime()).format('年')+datetime
        if re.match('\d+分钟前',datetime):
            minute=re.match('(\d+)',datetime).group(1)
            datetime=time.strftime('%Y{0}%m{1}%d{2} %H:%M',time.localtime(time.time()-float(minute)*60)).format('年','月','日')
        if re.match('今天.*',datetime):
            datetime=re.match('今天(.*)',datetime).group(1).strip()
            datetime=time.strftime('%Y{0}%m{1}%d{2}',time.localtime()).format('年','月','日')+' '+datetime
        return datetime

class MongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        #如果查询到数据就更新数据，如果没有就插入，做到item去重
        self.db[item.table_name].update({'id':item.get('id')},{'$set':dict(item)},True)
        return item