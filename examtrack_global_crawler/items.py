# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ExamtrackGlobalCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class UnivJournalItem(scrapy.Item):
    grad_school_name = scrapy.Field()
    major = scrapy.Field()
    grad_school_url = scrapy.Field()

class DaigakuinItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    grad_school_name = scrapy.Field()
    major = scrapy.Field()
    grad_school_url = scrapy.Field()
