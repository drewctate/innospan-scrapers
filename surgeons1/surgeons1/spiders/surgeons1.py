from __future__ import absolute_import
import scrapy
import time
import re
from surgeons1.items import SurgeonItem

def parseName(name):
    name = name.replace(',', '')
    name = name.replace('.', '')
    name = name.replace('"', '')
    names = name.split()
    return names

def addNameAndSuffix(item, name):
    parsedName = parseName(name)

    # remove suffixes
    allSuffixes = ['MD', 'DDS', 'DMD', 'II', 'III', 'Phd', 'PhD', 'Jr', 'FACS', 'PC']
    suffixes = []
    for word in parsedName:
        if word in allSuffixes:
            suffixes.append(word)
    parsedName = [x for x in parsedName if x not in suffixes]

    if len(parsedName) == 1:
        item['fname'] = parsedName[0]
    elif len(parsedName) == 2:
        item['fname'] = parsedName[0]
        item['lname'] = parsedName[1]
    elif len(parsedName) == 3:
        item['fname'] = parsedName[0]
        item['MI'] = parsedName[1]
        item['lname'] = parsedName[2]
    else:
        item['fname'] = parsedName[0]
        item['MI'] = parsedName[1]
        lname = ''
        for i in range(2, len(parsedName)):
            lname += ' ' + parsedName[i]
        item['lname'] = lname

    sufstr = ''
    for suffix in suffixes:
        sufstr += ' ' + suffix
    item['suffix'] = sufstr.strip()

class SurgeonSpider(scrapy.Spider):
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
        if response.xpath('//div[@class="body vcard tether_stats-track-impress"]'):
            for div in response.xpath('//div[@class="body vcard tether_stats-track-impress"]'):
                item = SurgeonItem()
                try:
                    if div.xpath('h4/text()'):
                        name = div.xpath('h4/text()').extract()[0]
                    else:
                        name = div.xpath('h4/a/text()').extract()[0]

                    addNameAndSuffix(item, name)
                    address = ''
                    addressParts = div.xpath('p//text()').extract()
                    for part in addressParts:
                        print part
                        address += part
                    item['address'] = address.strip()
                    item['phone'] = div.xpath('ul/li/div[@class="reveal-hidden"]/text()').extract()[0].replace('.', '-')
                except IndexError as e:
                    print e
                    pass
                yield item

            nextPage = response.xpath('//li[@class="pager-next pager-iteration"]/a/@href')
            if nextPage:
                url = response.urljoin(nextPage.extract()[0])
                yield scrapy.Request(url, callback=self.parseSurgeonList)

        elif response.xpath('//ul[@class="area_links"]//li/a/@href'):
            for href in response.xpath('//ul[@class="area_links"]//li/a/@href'):
                url = response.urljoin(href.extract())
                yield scrapy.Request(url, callback=self.parseCityList)

    def parseCityList(self, response):
        for th in response.xpath("//th[@scope='row']"):
            item = SurgeonItem()
            if th.xpath('h4/text()'):
                name = th.xpath('h4/text()').extract()[0]
            else:
                name = th.xpath('h4/a/text()').extract()[0]

            addNameAndSuffix(item, name)
            spans = th.xpath("address/span/text()")
            item['address'] = spans[0].extract().replace('\n', ' ') + ' ' + spans[1].extract().replace('\n', ' ')
            item['phone'] = th.xpath("address/span/span/text()").extract()
            yield item;

        nextPage = response.xpath("//a[contains(text(),'Next')]/@href")
        if nextPage:
            url = response.urljoin(nextPage.extract()[0])
            yield scrapy.Request(url, callback=self.parseCityList)
