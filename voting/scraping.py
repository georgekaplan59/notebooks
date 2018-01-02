# -*- coding: utf-8 -*-
from scrapy.crawler import CrawlerProcess
from spiders import RegionVotingSpider, LocalVotingSpider
from spider_helper_functions import get_province_for_regions_dict
import logging
import time
from constants import NO_PARTY_OPTION_LIST


def download_data_by_region():
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_URI': '../data/parlament_comarques_2015_%d.csv' % int(time.time()),
        'FEED_FORMAT': 'csv',
        'LOG_LEVEL': logging.INFO,
        'REGIONS': get_province_for_regions_dict(),
        'NO_PARTY_VOTES': NO_PARTY_OPTION_LIST
    })
    process.crawl(RegionVotingSpider)
    process.start()  # the script will block here until the crawling is finished
    process.stop()


def download_data_by_city(year=2015):
    domains = ['gencat.cat'] if year == 2015 else ['parlament2017.cat']
    start_urls = ['http://www.gencat.cat/governacio/resultatsparlament2015/resu/09AU/DAU09000CI_L1.htm'] if year == 2015 \
                 else ['https://resultats.parlament2017.cat/09AU/DAU09000CI.htm?lang=es']
    extractor_regex = 'DAU09\d+9CI_L1.htm' if year == 2015 else 'DAU09\d+9CI.htm'
    from_regex = 'DAU09(\d{2})9CI_L1.htm' if year == 2015 else 'DAU09(\d{2})9CI.htm'
    to_regex = 'IAU%s9MC_L1.htm' if year == 2015 else 'IAU%s9MC.htm'
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_URI': '../data/parlament_municipis_%d_%d.csv' % (year, int(time.time())),
        'FEED_FORMAT': 'csv',
        'LOG_LEVEL': logging.INFO,
        'NO_PARTY_VOTES': NO_PARTY_OPTION_LIST
    })
    process.crawl(LocalVotingSpider, domains=domains, start_urls=start_urls, extractor_regex=extractor_regex,
                  from_regex=from_regex, to_regex=to_regex)
    process.start()  # the script will block here until the crawling is finished
    process.stop()
