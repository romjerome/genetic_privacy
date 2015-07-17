import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from datetime import datetime
import pdb

class GeniSpider(CrawlSpider):
    name = "geni"
    allowed_domains = ["www.geni.com"]
    start_urls = ["http://www.geni.com/worldfamilytree"]
    rules = (
        Rule(LinkExtractor(allow = ("people\/\w+-\w+\/[0-9]+",)),
             callback="parse_person",
             # Follow links, even on pages we parse so that we follow to the
             # family member pages.
             follow = True),
    )

    def parse_person(self, response):
        item = PersonItem()
        
        full_name = response.xpath('//h2[@itemprop="name"]/text()').extract()
        name_parts = full_name.split()
        item["first_name"] = name_parts[0]
        if len(name_parts) is 3:
            item["middle_name"] = intern(name_parts[1])
            item["last_name"] = intern(name_parts[2])
        else:
            item["last_name"] = intern(name_parts[2])

        birth_date = response.xpath('//time[@id="birth_date"]/text()').extract()
        item["birth"] = datetime.strptime(birth_date, "%B %d, %Y")

        death_date = response.xpath('//td[@itemprop="death"]/time/text()').extract()
        item["death"] = datetime.strptime(death_date, "%B %d, %Y")
            
        family_url = ""
        request = scrapy.Request(family_url, callback=self.parse_family)
        request.meta["item"] = item
        yield request

    def parse_family(self, response, item):
        pass
