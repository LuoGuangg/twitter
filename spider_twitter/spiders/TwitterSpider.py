# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request,Spider
import json
import re
from scrapy import Selector
from lxml import etree
from ..items import SpiderTwitterItem
from spider_twitter.dbUtils import DBUtils
import time
import datetime


class TwitterSpider(scrapy.Spider):
    name = 'twitterSpider'

    db = DBUtils()

    now_time = datetime.datetime.now().strftime("%Y-%m-%d")

    url_spider = "https://twitter.com/i/profiles/show/{}/timeline/tweets?" \
                    "include_available_features=1&include_entities=1&reset_error_state=false"

    next_page_url = "https://twitter.com/i/search/timeline?vertical=default&q=from%3A{} since%3A2010-01-05 until%3A{}&src=typd&\
                        include_available_features=1&include_entities=1&max_position=TWEET-{}-{}&oldest_unread_id=0&reset_error_state=false"

    def start_requests(self):
        for name in self.db.getSeendNameAll():
            yield Request(url=self.url_spider.format(name[0]), callback=self.parse, meta={'spider_name': name[0]})

    def parse(self, response):
        sites = json.loads(response.text)

        spider_name = response.meta['spider_name']

        #网页html
        data = sites["items_html"]
        min_position = sites["min_position"]

        #第一条twitter
        position = ''

        if 'max_position' in sites:
            position = sites["max_position"]
        else:
            position = min_position.split('-')[2]


        if data == "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n \n":
            print ("抓取完成!!!,更新种子")
            self.db.updateSeedTag(spider_name)
            self.db.updateSeedCountLocation(spider_name, position)
        else:
            #是否还有下一页
            #has_more_items = sites["has_more_items"]

            item = SpiderTwitterItem()

            # 获得贴文作者
            twitter_author = re.compile('data-name="(.+)" data-user-id=').findall(data)[0]

            selector_app = Selector(text=data)
            twitter_group = selector_app.xpath("//li[@class='js-stream-item stream-item stream-item\n']").extract()
            twitter_group_count = len(twitter_group)

            next_page_id = ""

            for twitter_personal in twitter_group:
                selector_content = Selector(text=twitter_personal)
                twitter_id = selector_content.xpath("//li[@class='js-stream-item stream-item stream-item\n']/@data-item-id").extract()

                if len(twitter_id) > 0:
                    next_page_id = twitter_id[0]

                    if self.db.getTwitterById(next_page_id):

                        # 判断是否是爬取到之前记录位置
                        if self.db.isSeedLocation(spider_name, next_page_id):

                            print ("%s最新推文抓取完毕"%spider_name)
                            self.db.updateSeedCountLocation(spider_name, position)
                            return

                        print ("%s已存在,进行去重过滤"%next_page_id)
                        continue
                    else:
                        item['twitter_id'] = twitter_id

                else:
                    item['twitter_id'] = ''

                twitter_content_whole = ""
                twitter_content_list = selector_content.xpath("//div[@class='js-tweet-text-container']").extract()

                for twitter_content in twitter_content_list:
                    selector_content_text = Selector(text=twitter_content)
                    twitter_content_text = selector_content_text.xpath("//text()").extract()
                    twitter_content_text_num = len(twitter_content_text)
                    for i in range(twitter_content_text_num):
                        if twitter_content_text[i] != "  " and twitter_content_text[i] != "\n  ":
                            twitter_content_add = twitter_content_text[i].replace("\n","")
                            twitter_content_whole += twitter_content_add

                twitter_content_whole_trun = twitter_content_whole.replace('"','\\"')
                twitter_href = selector_content.xpath("//small[@class='time']/a/@href").extract()
                twitter_time = selector_content.xpath("//small[@class='time']/a/@title").extract()
                twitter_num = selector_content.xpath("//span[@class='ProfileTweet-actionCountForAria']/text()").extract()
               
                if len(twitter_num) > 0:
                    twitter_reply = twitter_num[0]
                    twitter_trunsmit = twitter_num[1]
                    twitter_zan = twitter_num[2]
                else:
                    twitter_reply = ''
                    twitter_trunsmit = ''
                    twitter_zan = ''

                twitter_img = selector_content.xpath("//div[@class='AdaptiveMedia-photoContainer js-adaptive-photo ']/@data-image-url").extract()
                print ("目标:%s" % twitter_id[0])
                print ("内容:%s" % twitter_content_whole_trun)
                if len(twitter_author) > 0:
                    author = twitter_author
                    item['twitter_author'] = author
                else:
                    item['twitter_author'] = ''
                if len(twitter_id) > 0:
                    tw_id = twitter_id[0]
                    item['twitter_id'] = tw_id
                else:
                    item['twitter_id'] = ''
                if twitter_content_whole:
                    content = twitter_content_whole_trun
                    item['twitter_content'] = content
                else:
                    item['twitter_content'] = ''
                if len(twitter_href) > 0:
                    href = "https://twitter.com%s"%twitter_href[0]
                    item['twitter_href'] = href
                else:
                    item['twitter_href'] = ''
                if len(twitter_time) > 0:
                    time = twitter_time[0]
                    item['twitter_time'] = time
                else:
                    item['twitter_time'] = ''
                if len(twitter_num) > 0:
                    reply = twitter_reply
                    item['twitter_reply'] = reply
                else:
                    item['twitter_reply'] = ''
                if len(twitter_num) > 0:
                    trunsmit = twitter_trunsmit
                    item['twitter_trunsmit'] = trunsmit
                else:
                    item['twitter_trunsmit'] = ''
                if len(twitter_num) > 0:
                    zan = twitter_zan
                    item['twitter_zan'] = zan
                else:
                    item['twitter_zan'] = ''
                if len(twitter_img) == 1:
                    img = twitter_img[0]
                    item['twitter_img'] = img
                elif len(twitter_img) > 1:
                    img_list = []
                    for img in twitter_img:
                        img_list.append(img)
                    item['twitter_img'] = img_list
                else:
                    item['twitter_img'] = ''
                yield item

            print ("下一页等待中...")

            #has_more_items 为true 代表还有下一页
            yield Request(url=self.next_page_url.format(spider_name,self.now_time, next_page_id, position), callback=self.parse,headers={'Referer': "https://twitter.com/"}, meta={'spider_name': spider_name})


