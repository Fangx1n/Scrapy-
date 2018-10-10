# -*- coding: utf-8 -*-
import re
import scrapy
import tushare as ts
from ..items import WeiboItem


class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['weibo.cn']
    search_url = 'https://weibo.cn/search/mblog'
    max_page=100

    def start_requests(self):
        result=ts.get_hs300s()
        keywords=result['code'].tolist()
        for keyword in keywords:
            url='{url}?keyword={keyword}'.format(url=self.search_url,keyword=keyword)
            print('正在请求：'+url)
            for page in range(self.max_page+1):
                data={
                    'mp':str(self.max_page),
                    'page':str(page),
                }
                yield scrapy.FormRequest(url,callback=self.parse_index,formdata=data,meta={'keyword':keyword})

    def parse_index(self, response):
        #headers中删除cookies，否则会报400
        # print(response.text)
        weibos=response.xpath('//div[@class="c" and contains(@id,"M_")]')
        for weibo in weibos:
            #判断是否是转发的微博  true为转发的微博，false为原创微博class为ctt
            is_forword=bool(weibo.xpath('.//span[@class="cmt"]').extract_first())
            print(is_forword)
            if is_forword:
                detail_url=weibo.xpath('.//a[contains(., "原文评论[")]//@href').extract_first()
            else:
                detail_url=weibo.xpath('.//a[contains(., "评论[")]//@href').extract_first()
            print(detail_url)
            yield scrapy.Request(detail_url,callback=self.parse_detail,meta={"keyword":response.meta['keyword']})


    def parse_detail(self, response):
        #每条微博的id,是一串不重复的数字
        id=re.search('comment\/(.*?)\?',response.url).group(1)
        #当前页面的url
        url=response.url
        #微博中会有a标签的链接（#今日看盘[超话]# #上证指数 sh000001# @微博股票 等等这些信息），extract_first只返回列表第一个元素，用join函数拼接起来
        content=''.join(response.xpath('//div[@id="M_"]//span[@class="ctt"]//text()').extract_first())
        print(id,url,content)
        #评论数
        comment_count=response.xpath('//span[@class="pms"]//text()').re_first('评论\[(.*?)\]')
        #转发数
        forword_count=response.xpath('//a[contains(.,"转发[")]//text()').re_first('转发\[(.*?)\]')
        #点赞数
        like_count=response.xpath('//a[contains(.,"赞[")]//text()').re_first('赞\[(.*?)\]')
        #微博发表时间
        posted_at=response.xpath('//div[@id="M_"]//span[@class="ct"]//text()').extract_first(default=None)
        #博主
        user=response.xpath('//div[@id="M_"]/div[1]/a/text()').extract_first(default=None)
        print(comment_count,forword_count,like_count,posted_at,user)

        keyword=response.meta['keyword']
        weibo_item=WeiboItem()
        for field in weibo_item.fields:
            try:
                weibo_item[field]=eval(field)
            except NameError:
                self.logger.debug('Field is Not Defined：'+ field)
        yield weibo_item