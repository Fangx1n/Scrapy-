# -*- coding: utf-8 -*-
import json

import scrapy

# from Scrapy项目.zhihuuser.zhihuuser.items import UserItem
from ..items import UserItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    #设置要爬取的大V主页名字
    start_user='excited-vczh'

    #大V的信息
    user_url='https://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_query='allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics'

    #大V的关注列表
    follows_url='https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    follows_query='data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    #大V的粉丝列表
    followers_url='https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit={limit}'
    followers_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    def start_requests(self):
        # url='https://www.zhihu.com/api/v4/members/yinzhangqi?include=allow_message%2Cis_followed%2Cis_following%2Cis_org%2Cis_blocking%2Cemployments%2Canswer_count%2Cfollower_count%2Carticles_count%2Cgender%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'
        # url='https://www.zhihu.com/api/v4/members/excited-vczh/followers?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset=0&limit=20'
        #获取自己的信息
        yield scrapy.Request(self.user_url.format(user=self.start_user,include=self.user_query),self.parse_user)
        #获取关注列表
        yield scrapy.Request(self.follows_url.format(user=self.start_user,include=self.follows_query,offset=0,limit=20),callback=self.parse_follows)
        #获取粉丝列表
        yield scrapy.Request(self.followers_url.format(user=self.start_user,include=self.followers_query,offset=0,limit=20),callback=self.parse_followers)

    #获取自己信息
    def parse_user(self, response):
        results=json.loads(response.text)
        item=UserItem()
        for field in item.fields:
            if field in results.keys():
                item[field]=results.get(field)
        yield item
        #获取大V关注列表的人自己的关注列表
        yield scrapy.Request(self.follows_url.format(user=results.get('url_token'),include=self.follows_query,limit=20,offset=0),self.parse_follows)
        #获取大V关注列表的人自己的粉丝列表
        yield scrapy.Request(self.followers_url.format(user=results.get('url_token'),include=self.followers_query,limit=20,offset=0),self.parse_followers)

    #获取关注列表
    def parse_follows(self,response):
        results = json.loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data'):
                yield scrapy.Request(self.user_url.format(user=result.get('url_token'),include=self.user_query),callback=self.parse_user)
        #继续获取下一页
        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page=results.get('paging').get('next')
            yield scrapy.Request(next_page,self.parse_follows)

    #获取粉丝列表
    def parse_followers(self,response):
        results = json.loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data'):
                yield scrapy.Request(self.user_url.format(user=result.get('url_token'),include=self.user_query),callback=self.parse_user)
        # 继续获取下一页
        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page=results.get('paging').get('next')
            yield scrapy.Request(next_page,self.parse_followers)