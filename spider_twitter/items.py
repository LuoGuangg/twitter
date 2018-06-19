# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SpiderTwitterItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    twitter_id = scrapy.Field()
    twitter_author = scrapy.Field()
    twitter_content = scrapy.Field()
    twitter_href = scrapy.Field()
    twitter_time = scrapy.Field()
    twitter_reply = scrapy.Field()
    twitter_trunsmit = scrapy.Field()
    twitter_zan = scrapy.Field()
    twitter_img = scrapy.Field()
