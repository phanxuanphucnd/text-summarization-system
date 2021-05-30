# -*- coding: utf-8 -*-

from scrapy import Spider
from scrapy.http import Request
from news.items import NewsItems
from news.loader import NewsLoader

'''
Spider class for crawl pages
'''
class VietinbankSpider(Spider):
    # Crawling CafeF example
    name = 'Vietinbank'

    # scrapy crawl Vietinbank -a group=banking -a start_url=https://www.vietinbank.vn/vn/tin-tuc \
    # -a root_url=https://www.vietinbank.vn -a next_link="https://www.vietinbank.vn/vn/tin-tuc?page={0}"

    page = 2
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

        if self.limit > 0 and self.num_news > self.limit:
            return
        # self.num_news += 1
        next_page = self.next_link.format(self.page)
        self.page += 1
        links = response.xpath("//div[@id='top-news-list']/a[@class='link-topnews']/@href").getall()
        links = ["".join([self.root_url, x]) for x in links]
        current_page = response.xpath("//li[@class='currentitem']/strong/text()").get()
        if int(current_page) == self.page - 2:
            yield Request(
                url=next_page,
                callback=self.parse_list_page
            )

        for news_link in links:
            yield Request(
                url=news_link,
                callback=self.extract_news
            )

    def extract_news(self, response):
        """Function to extract content of new from html

        :param response: raw data of a news page
        
        """
        if (self.limit > 0 and self.num_news > self.limit) or self.force_stop:
            return
        self.num_news += 1
        item = NewsLoader(item=NewsItems(), response=response, date_fmt=["%d/%m/%Y %H:%M"],
                          date_regex="((\d{1,2})/(\d{1,2})/(\d{4}) (\d{2}):(\d{2}))")
        entry = response.xpath("//div[@id='articles']")[0]
        title = entry.xpath(".//h1[@class='black padding10000']/text()").get().strip()
        created_date = entry.xpath(".//div[@class='articles-title']/span[@class='date']/text()").get().strip()
        source_url = response.request.url
        try:
            brief_content = "".join(entry.xpath(".//span/div[@class='bold gray']/p/descendant::text()").getall()).strip()
        except:
            brief_content = title
        if len(brief_content) == 0:
            brief_content = title
        main_content = ""
        try:
            for p in entry.xpath(".//p"):
                main_content = main_content + "\n" + "".join(p.xpath("./descendant::text()").getall()).strip()
            main_content = main_content.strip()
        except:
            pass
        if len(main_content) == 0:
            main_content = brief_content
        category = self.group
        if len(brief_content) == 0:
            brief_content = title
        item.add_value("title", title)
        item.add_value("published_date", item.find_published_date(created_date))
        item.add_value("source_url", source_url)
        item.add_value("brief_content", brief_content)
        item.add_value("content", main_content)
        item.add_value("category", category)
        item.add_value("site", "https://www.vietinbank.vn")

        from datetime import datetime
        import pytz
        today = datetime.now(pytz.timezone('Asia/Bangkok')).replace(tzinfo=None)
        item.add_value("created_at", today)

        yield item.load_item()
