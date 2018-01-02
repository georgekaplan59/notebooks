import scrapy
from constants import *


class VotesByRegionItem(scrapy.Item):
    Option = scrapy.Field()
    Votes = scrapy.Field()
    Region = scrapy.Field()
    Constituency = scrapy.Field()


class VotesByTownItem(scrapy.Item):
    Option = scrapy.Field()
    Votes = scrapy.Field()
    City = scrapy.Field()
    Constituency = scrapy.Field()


def build_data_item(option, votes, constituency, city=None, region=None):
    data_item = VotesByTownItem() if city else VotesByRegionItem()
    data_item[OPTION] = option
    data_item[VOTES] = votes
    data_item[CONSTITUENCY] = constituency
    if city:
        data_item[CITY] = city
    if region:
        data_item[REGION] = region
    return data_item
