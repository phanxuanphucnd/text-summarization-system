# -*- coding: utf-8 -*-

from scrapy import Spider
from scrapy.http import Request
from news.items import NewsItems
from news.loader import NewsLoader

'''
Spider class for crawl pages
'''


class CafeFSpider(Spider):
    # Crawling CafeF example
    name = 'CafeF'

    # scrapy crawl CafeF -a group=macro -a start_url=https://cafef.vn/vi-mo-dau-tu.chn \
    # -a root_url=https://cafef.vn -a next_link="https://cafef.vn/timeline/33/trang-{0}.chn"

    page = 1
    num_news = 0
    limit = -1

    def __init__(self, category='', **kwargs):
        super().__init__(**kwargs)
        if self.limit != -1:
            self.limit = int(self.limit)
        self.force_stop = False

    def start_requests(self):
        yield Request(
            url=self.start_url,
            callback=self.parse_list_page
        )

    def parse_list_page(self, response):
        """ This spider would start with page, collecting category links, and item links, 
        parsing the latter with this function method

        :param response: response of the start page

        """

        if (self.limit > 0 and self.num_news > self.limit) or self.force_stop:
            return
        next_page = self.next_link.format(self.page)
        self.page += 1
        # print(self.page, next_page)
        news_links = []
        links = response.xpath("//li[contains(@class, 'tlitem')]/h3/a/@href").getall()
        # links = entry.xpath(".//h3/a/@href").extract()
        for link in links:
            link = self.root_url + link
            if link not in news_links:
                news_links.append(link)

        for news_link in news_links:
            yield Request(
                url=news_link,
                callback=self.extract_news
            )

        if len(news_links) != 0:
            yield Request(
                url=next_page,
                callback=self.parse_list_page
            )


    def extract_news(self, response):
        """Function to extract content of new from html

        :param response: raw data of a news page
        
        """
        if self.limit > 0 and self.num_news > self.limit:
            return
        self.num_news += 1
        item = NewsLoader(item=NewsItems(), response=response, date_fmt=["%d-%m-%Y - %H:%M %p"],
                          date_regex="((\d{2})-(\d{2})-(\d{4}) - (\d{2}):(\d{2}) (AM|PM))")
        entry = response.xpath("//div[@class='left_cate totalcontentdetail']")[0]
        title = entry.xpath(".//h1[@class='title']/text()").get().strip()
        created_date = entry.xpath(".//span[@class='pdate']/text()").get().strip()
        source_url = response.request.url
        try:
            brief_content = "".join(entry.xpath(".//h2[@class='sapo']/descendant::text()").getall()).strip()
        except:
            brief_content = title
        if len(brief_content) == 0:
            brief_content = title
        main_content = ""
        for p in entry.xpath(".//span[@id='mainContent']/p"):
            main_content = "\n".join([main_content, "".join(p.xpath("./descendant::text()").getall()).strip()])
        if len(main_content) == 0:
            main_content = brief_content
        category = self.group

        item.add_value("title", title)
        item.add_value("published_date", item.find_published_date(created_date))
        item.add_value("source_url", source_url)
        item.add_value("brief_content", brief_content)
        item.add_value("content", main_content)
        item.add_value("category", category)
        item.add_value("site", "https://cafef.vn")

        from datetime import datetime
        import pytz
        today = datetime.now(pytz.timezone('Asia/Bangkok')).replace(tzinfo=None)
        item.add_value("created_at", today)

        yield item.load_item()
