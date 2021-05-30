# -*- coding: utf-8 -*-

import time
from scrapy import Spider
from scrapy import Request
from news.items import NewsItems
from news.loader import NewsLoader


class ZingnewsSpider(Spider):
    """Zingnews"""

    # scrapy crawl zingnews -a group='social_trend' -o ./zingnews.csv -a limit=5000

    name = "zingnews"
    allowed_domains = ["zingnews.vn"]
    start_url = "https://zingnews.vn/xu-huong.html"
    group = "social_trend"

    count = 0
    limit = -1

    def __init__(self, category='', **kwargs):
        super().__init__(**kwargs)
        if self.limit != -1:
            self.limit = int(self.limit)

    def start_requests(self):
        yield Request(url=self.start_url, callback=self.parse)

    def parse(self, response):
        """ This spider would start with page, collecting category links, and item links, 
        parsing the latter with this function method

        :param response: response of the start page

        """

        if (self.limit > 0 and self.count > self.limit):
            return

        # extract news
        urls = response.xpath('//*[@class="article-title"]/a/@href').getall()

        next_page = response.xpath('//*[@class="btnMore"]/a/@href').get()

        for url in urls:
            if self.count > self.limit and self.limit > 0:
                return

            connect_to_url = response.urljoin(url)
            yield Request(url=connect_to_url, callback=self.parse_content)

        if next_page:
            if self.count > self.limit and self.limit > 0:
                return
            next_url = response.urljoin(next_page)
            print('next_url: ', next_url)
            yield Request(next_url, callback=self.parse)

    def parse_content(self, response):
        """Function to extract content of new from html

        :param response: raw data of a news page
        
        """

        if self.limit > 0 and self.count > self.limit:
            return

        self.count += 1

        item = NewsLoader(item=NewsItems(), response=response, date_fmt=["%-d/%-m/%Y, %H:%M"],
                          date_regex="((\d{1,2})/(\d{1,2})/(\d{4}) (\d{2}):(\d{2}))")

        category = self.group
        source_url = response.request.url
        title = response.xpath("//*[@class='the-article-title']/text()").get().strip()
        created_date = response.xpath("//*[@class='the-article-publish']/text()").get().strip()
        brief_content = response.xpath("//*[@class='the-article-summary']/text()").get().strip()

        main_content = response.css(".the-article-body >p::text").getall()
        main_content = "\n".join(ct.strip() for ct in main_content if ct.strip() != '')

        item.add_value("title", title)
        item.add_value("published_date", item.find_published_date(created_date))
        print(item.find_published_date(created_date))
        item.add_value("source_url", source_url)
        item.add_value("brief_content", brief_content)
        item.add_value("content", main_content)
        item.add_value("category", category)
        item.add_value("site", "https://zingnews.vn/")

        yield item.load_item()