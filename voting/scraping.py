# -*- coding: utf-8 -*-
from scrapy.crawler import CrawlerProcess
import logging
from spiders import RegionVotingSpider, LocalVotingSpider
from spider_helper_functions import get_province_for_regions_dict, get_list_of_no_voting_options
import time


def download_data_by_region():
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_URI': '../data/parlament_comarques_2015_%d.csv' % int(time.time()),
        'FEED_FORMAT': 'csv',
        'LOG_LEVEL': logging.INFO,
        'REGIONS': get_province_for_regions_dict(),
        'NO_PARTY_VOTES': get_list_of_no_voting_options()
    })
    process.crawl(RegionVotingSpider)
    process.start()  # the script will block here until the crawling is finished
    process.stop()


def download_data_by_city():
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_URI': '../data/parlament_municipis_2015_%d.csv' % int(time.time()),
        'FEED_FORMAT': 'csv',
        'LOG_LEVEL': logging.INFO,
        'NO_PARTY_VOTES': get_list_of_no_voting_options()
    })
    process.crawl(LocalVotingSpider)
    process.start()  # the script will block here until the crawling is finished
    process.stop()
