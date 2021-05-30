# -*- coding: utf-8 -*-

import re
import scrapy
from scrapy.http import Request
from news.items import NewsItems
from news.loader import NewsLoader


class VcbSpider(scrapy.Spider):
    name = "vcb"
    allowed_domains = ["portal.vietcombank.com.vn"]

    group = 'banking_group'

    count = 0
    limit = -1

    start_urls = [
        "https://portal.vietcombank.com.vn/News/Pages/home.aspx"
    ]

    def __init__(self, category="", **kwargs):
        super().__init__(**kwargs)

        if self.limit != -1:
            self.limit = int(self.limit)

    def parse(self, response):
        """ This spider would start with page, collecting category links, and item links, 
        parsing the latter with this function method

        :param response: response of the start page

        """

        # urls_hot_news = response.css(".hot-news .right .mCSB_container .ui-tabs-nav-item ::attr(href)").getall()
        # urls_body_first = response.css(".body .left .box-news-home .content .first ::attr(href)").getall()
        # urls_body_other = response.css(".body .left .box-news-home .content .other ::attr(href)").getall()
        # urls = urls_body_first + urls_body_other

        urls = response.css(".body .left .box-news-home .content .more ::attr(href)").getall()

        for url in urls:
            if self.limit < 0 or self.count < self.limit:
                connect_to_url = response.urljoin(url)
                yield Request(connect_to_url, callback=self.parse_page)
            else:
                break

    def parse_page(self, response):

        urls = response.css('.title >a ::attr(href)').getall()
        print('urls: ', urls)
        next_page = response.xpath(
            '//*[@id="ctl00_ctl10_g_befd5052_71f7_4441_9923_cb39f14d82e9"]/div/div[2]/div[2]/a[6]/@href').get()

        for url in urls:
            if self.count < self.limit or self.limit < 0:
                connect_to_url = response.urljoin(url)
                yield Request(connect_to_url, callback=self.parse_content)
            else:
                break

        if next_page and self.count < self.limit or self.limit < 0:
            next_url = response.urljoin(next_page)

            yield Request(next_url, callback=self.parse_page)

    def parse_content(self, response):
        """Function to extract content of new from html

        :param response: raw data of a news page
        
        """

        # item = NewsLoader(item=NewsItems(), response=response, date_fmt=["%m/%d/%y"])

        if self.limit > 0 and self.count > self.limit:
            return
        self.count += 1

        item = NewsLoader(item=NewsItems(), response=response, date_fmt=["%d/%m/%Y %H:%M %p"],
                          date_regex="((\d{2})/(\d{2})/(\d{4}) (\d{2}):(\d{2}) (AM|PM))")

        category = self.group
        source_url = response.request.url

        title = response.xpath('//*[@id="titleNews"]/text()').get().strip()
        published_date = response.xpath('//*[@class="time"]/text()').get().strip()
        published_date = re.sub(r'CH', 'PM', published_date)
        published_date = re.sub(r'SA', 'AM', published_date)
        brief_content = " ".join(response.xpath('//*[@class="news-description"]/descendant::text()').getall()).strip()

        content = response.css('.news-content .content-news ::text').getall()

        item.add_value('title', title)
        item.add_value('category', category)
        item.add_value('source_url', source_url)
        item.add_value('published_date', published_date)

        if brief_content:
            item.add_value('brief_content', brief_content.strip())
        item.add_value('content', "\n".join(nd.strip() for nd in content))
        item.add_value("site", "https://portal.vietcombank.com.vn")

        from datetime import datetime
        import pytz
        today = datetime.now(pytz.timezone('Asia/Bangkok')).replace(tzinfo=None)
        item.add_value("created_at", today)

        yield item.load_item()
