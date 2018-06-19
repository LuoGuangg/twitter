# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from spider_twitter.dbUtils import DBUtils

class SpiderTwitterPipeline(object):
    def process_item(self, item, spider):
        db = DBUtils()
        db.saveTwitter(item)
        return item
