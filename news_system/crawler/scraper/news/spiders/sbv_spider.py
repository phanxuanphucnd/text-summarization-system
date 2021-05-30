# -*- coding: utf-8 -*-

import scrapy
from scrapy.http import Request
from news.items import NewsItems
from news.loader import NewsLoader


class SbvSpider(scrapy.Spider):
    name = "sbv"
    allowed_domains = ["www.sbv.gov.vn"]

    group = 'banking_group'

    count = 0
    limit = -1

    start_url = "https://www.sbv.gov.vn/webcenter/portal/vi/menu/trangchu/ttsk"


    def __init__(self, category="", **kwargs):
        super().__init__(**kwargs)

        if self.limit != -1:
            self.limit = int(self.limit)

    def start_requests(self):
        yield Request(
            url=self.start_url,
            callback=self.parse
        )

    def parse(self, response):
        """ This spider would start with page, collecting category links, and item links, 
        parsing the latter with this function method

        :param response: response of the start page

        """
        urls = response.css("div.x29m a.xfu::attr(href)").getall()

        next_page = response.xpath('//*[@id="T:oc_9259810424region:gl5"]/@href').get()
        # next_page = [self.start_urls[0] + i for i in next_page]

        # next_page = ''.join(map(str, next_page))

        # headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
        print(f"URLs: {urls}")

        for url in urls:
            if self.count < self.limit or self.limit < 0:
                connect_to_url = response.urljoin(url)
                yield Request(connect_to_url, callback=self.parse_content)
            else:
                break

        if next_page and self.count < self.limit or self.limit < 0:
            next_url = response.urljoin(next_page)

            yield Request(next_url, callback=self.parse)

    def parse_content(self, response):
        """Function to extract content of new from html

        :param response: raw data of a news page
        
        """

        # item = NewsLoader(item=NewsItems(), response=response, date_fmt=["%m/%d/%y"])

        item = NewsLoader(item=NewsItems(), response=response, date_fmt=["%d/%m/%Y"],
                          date_regex="((\d{2})/(\d{2})/(\d{4})")

        self.count += 1

        category = self.group
        source_url = response.request.url
        title = response.xpath('//*[@id="T:oc_7115552043region:pbl6"]/text()').get()
        published_date = response.xpath('//*[@id="T:oc_7115552043region:j_id__ctru16pc8"]/label/text()').get()
        try:
            brief_content = "".join(response.xpath('//*[@id="pbl20"]/descendant::text()').getall()).strip()
        except Exception as e:
            print('Error: ', e)
        content = ""
        for p in response.xpath('//*[@id="pbl21"]/div/p/span'):
            content = content + "\n" + "".join(p.xpath('./descendant::text()').getall()).strip()

        item.add_value('title', title)
        item.add_value('category', category)
        item.add_value('source_url', source_url)
        item.add_value('published_date', published_date)

        if brief_content:
            item['brief_content'] = brief_content.strip()
        item.add_value('content', content)
        item.add_value("site", "https://www.sbv.gov.vn")

        from datetime import datetime
        import pytz
        today = datetime.now(pytz.timezone('Asia/Bangkok')).replace(tzinfo=None)
        item.add_value("created_at", today)

        yield item.load_item()