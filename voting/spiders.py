from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy import Request
from items import build_data_item
from spider_helper_functions import *
import re


class LocalVotingSpider(CrawlSpider):

    name = 'parlament_municipis'
    allowed_domains = ['gencat.cat']
    start_urls = ['http://www.gencat.cat/governacio/resultatsparlament2015/resu/09AU/DAU09000CI_L1.htm']
    rules = [Rule(LinkExtractor(allow=['DAU09\d+9CI_L1.htm']), 'load_iframe')]

    def get_province_code(self, url):
        code_matched = re.search('DAU09(\d{2})9CI_L1.htm', url)
        return code_matched.group(1)

    def get_province(self, response):
        return response.xpath("//div[@class='divmuni']/ul/li/a[@class='act']/text()").extract()[0]

    def get_town(self, response):
        town = response.xpath("//div[@id='titulo']/text()").extract()[0]
        if town.startswith('-'):
            town = town[1:-1]
        return town

    def load_iframe(self, response):
        province_url = response.url.split('/')[-1]
        province_code = self.get_province_code(province_url)
        url = response.urljoin('IAU%s9MC_L1.htm' % province_code)
        yield Request(url, callback=self.link_town)

    def link_town(self, response):
        for href in response.xpath("//div[@class='divmuni']/ul/li/a/@href"):
            url = response.urljoin(href.extract())
            yield Request(url, callback=self.parse_votes)

    def parse_votes(self, response):
        no_party_votes = self.settings['NO_PARTY_VOTES']
        town = self.get_town(response)
        province = self.get_province(response)

        for antivote_row in response.xpath("//table[@id='TVGEN']/tbody/tr"):
            category = get_antivote_category(antivote_row)
            if category in no_party_votes:
                data_item = build_data_item(category, get_antivotes(antivote_row), province, municipio=town)
                if data_item['votos'] > 0:
                    yield data_item

        for row in response.xpath("//table[@id='TVOTOS']/tbody/tr"):
            data_item = build_data_item(get_party(row), get_votes(row), province, municipio=town)
            if data_item['votos'] > 0:
                yield data_item


class RegionVotingSpider(CrawlSpider):

    name = 'parlament_comarques'
    allowed_domains = ['gencat.cat']
    start_urls = ['http://www.gencat.cat/governacio/resultatsparlament2015/resu/09AU/DAU09000CR_L1.htm']
    rules = [Rule(LinkExtractor(allow=['DAU09\d+9CR_L1.htm']), 'parse_votes')]

    def parse_votes(self, response):
        region_province_dict = self.settings['REGIONS']
        no_party_votes = self.settings['NO_PARTY_VOTES']
        region = response.xpath("//div[@id='titulo']/text()").extract()[0]
        province = region_province_dict[region] if region in region_province_dict else 'NA'
        if province == 'NA':
            print("Region: %s (%s)" % (region, region_province_dict.keys()))

        for antivote_row in response.xpath("//table[@id='TVGEN']/tbody/tr"):
            category = get_antivote_category(antivote_row)
            if category in no_party_votes:
                data_item = build_data_item(category, get_antivotes(antivote_row), province, comarca=region)
                if data_item['votos'] > 0:
                    yield data_item

        for row in response.xpath("//table[@id='TVOTOS']/tbody/tr"):
            data_item = build_data_item(get_party(row), get_votes(row), province, comarca=region)
            if data_item['votos'] > 0:
                yield data_item
