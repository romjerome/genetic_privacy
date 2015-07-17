# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PersonItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    first_name = scrapy.Field()
    last_name = scrapy.Field()
    middle_name = scrapy.Field()
    birth = scrapy.Field()
    death = scrapy.Field()
    mother = scrapy.Field()
    father = scrapy.Field()
    children = scrapy.Field()
