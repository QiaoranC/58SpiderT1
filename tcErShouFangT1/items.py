# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Tcershoufangt1Item(scrapy.Item):
    keywords = scrapy.Field()
    title = scrapy.Field()
    name = scrapy.Field()
    description = scrapy.Field()
    imgs = scrapy.Field()
    url = scrapy.Field()
    position_city = scrapy.Field()
    position_district = scrapy.Field()
    position_commercial_area = scrapy.Field()
    position_detail = scrapy.Field()
    contact_name = scrapy.Field()
    phone = scrapy.Field()
    refresh_at = scrapy.Field()
    details = scrapy.Field()
    views = scrapy.Field()
    price = scrapy.Field()
    allocation = scrapy.Field()
    pack = scrapy.Field()
    price_unit = scrapy.Field()
    owner_type = scrapy.Field()
    room = scrapy.Field()
    acerage = scrapy.Field()
    batch = scrapy.Field()
    data_id = scrapy.Field()
    category_second_id = scrapy.Field()
    type = scrapy.Field()
    rent_mode = scrapy.Field()
    list_item_pack = scrapy.Field()
    house_type = scrapy.Field()
    category = scrapy.Field()
    trade = scrapy.Field()
