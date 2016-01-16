from __future__ import absolute_import
import scrapy
import time
from surgeons1.items import SurgeonItem

class DmozSpider(scrapy.Spider):
    name = "surgeons1"
    allowed_domains = ["surgery.org", "smartbeautyguide.com"]
    start_urls = [
        "http://www.surgery.org/consumers/find-a-plastic-surgeon",
    ]

    def parse(self, response):
        surgeonLists = []
        for l in response.xpath('//div[@class="column left"]//a/@href').extract() + response.xpath('//div[@class="column right"]//a/@href').extract():
            time.sleep(.2)
            url = response.urljoin(l)
            yield scrapy.Request(url, callback=self.parseSurgeonList)

    def parseSurgeonList(self, response):
        for div in response.xpath('//div[@class="body vcard tether_stats-track-impress"]'):
            item = SurgeonItem()
            try:
                if div.xpath('h4/text()'):
                    item['name'] = div.xpath('h4/text()').extract()[0]
                else:
                    item['name'] = div.xpath('h4/a/text()').extract()[0]
                item['address'] = div.xpath('p/text()').extract()[0]
                item['phone'] = div.xpath('ul/li/div[@class="reveal-hidden"]/text()').extract()[0]
            except IndexError as e:
                print e
                pass
            yield item

        nextPage = response.xpath('//li[@class="pager-next pager-iteration"]/a/@href')
        if nextPage:
            url = response.urljoin(nextPage.extract()[0])
            yield scrapy.Request(url, callback=self.parseSurgeonList)