from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy import Request
from items import build_data_item
from constants import *
from spider_helper_functions import *
import re


class LocalVotingSpider(CrawlSpider):

    name = 'parlament_municipis'

    def __init__(self, domains=None, start_urls=None, extractor_regex=None, from_regex=None, to_regex=None,
                 *args, **kwargs):
        self.allowed_domains = domains
        self.start_urls = start_urls
        self.rules = [Rule(LinkExtractor(allow=extractor_regex), 'load_iframe')]
        self.from_regex = from_regex
        self.to_regex = to_regex
        super(LocalVotingSpider, self).__init__(*args, **kwargs)

    def load_iframe(self, response):
        province_url = response.url.split('/')[-1]
        province_code = self.get_province_code(province_url)
        url = response.urljoin(self.to_regex % province_code)
        yield Request(url, callback=self.link_town)

    def get_province_code(self, url):
        code_matched = re.search(self.from_regex, url)
        return code_matched.group(1)

    def get_province_town(self, response, version=2015):
        return self.get_province_town_2015(response) if version == 2015 else self.get_province_town_2017(response)

    def get_province_town_2015(self, response):
        province = response.xpath("//div[@class='divmuni']/ul/li/a[@class='act']/text()").extract()[0]
        town = response.xpath("//div[@id='titulo']/text()").extract()[0]
        if town.startswith('-'):
            town = town[1:-1]
        return province, town

    def get_province_town_2017(self, response):
        xpath_base = "//span[@id='ambito']/span/"
        town = response.xpath(xpath_base + "span[@id='ambitoSuperior1']/text()").extract()[0].strip()
        province = response.xpath(xpath_base + "span[@class='ambitoSuperior3']/span[@lang='es']/text()").extract()[0]
        province = province.split("de ")[1].strip()
        return province, town

    def link_town(self, response):
        for href in response.xpath("//div[@class='divmuni']/ul/li/a/@href"):
            url = response.urljoin(href.extract())
            yield Request(url, callback=self.parse_votes)

    def parse_votes(self, response):
        no_party_votes = self.settings['NO_PARTY_VOTES']
        version = 2015 if 'gencat.cat' in self.allowed_domains else 2017
        province, town = self.get_province_town(response, version)
        antivote_xpath = "./th/text()" if version == 2015 else "./th/span[@lang='es']/text()"
        votes_xpath = "./td[@class='vots s15']/text()" if version == 2015 else "./td[contains(@class,'vots s15')]/text()"
        number_of_elements = 2 if version == 2015 else 1

        for antivote_row in response.xpath("//table[@id='TVGEN']/tbody/tr"):
            category = get_antivote_category(antivote_row, antivote_xpath)
            if category in no_party_votes:
                votes = get_antivotes(antivote_row, number_of_elements)
                data_item = build_data_item(category, votes, province, city=town)
                if data_item[VOTES] > 0:
                    yield data_item

        for row in response.xpath("//table[@id='TVOTOS']/tbody/tr"):
            data_item = build_data_item(get_party(row), get_votes(row, votes_xpath), province, city=town)
            if data_item[VOTES] > 0:
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
                data_item = build_data_item(category, get_antivotes(antivote_row), province, region=region)
                if data_item[VOTES] > 0:
                    yield data_item

        for row in response.xpath("//table[@id='TVOTOS']/tbody/tr"):
            data_item = build_data_item(get_party(row), get_votes(row), province, region=region)
            if data_item[VOTES] > 0:
                yield data_item
