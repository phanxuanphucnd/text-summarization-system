# -*- coding: utf-8 -*-

from scrapy import Spider
from scrapy.http import Request
from news.items import NewsItems
from news.loader import NewsLoader

import logging

'''
Spider class for crawl pages
'''
class VietnambizSpider(Spider):
    # Crawling Vietnambiz class
    name = 'Vietnambiz'

    # scrapy crawl Vietnambiz -a group=macro -a start_url=https://vietnambiz.vn/thoi-su/vi-mo.htm \
    # -a root_url=https://vietnambiz.vn -a next_link="https://vietnambiz.vn/thoi-su/vi-mo/trang-{0}.htm"

    # start scroll position
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
        if (self.limit > 0 and self.num_news > self.limit) or self.force_stop:
            return
        next_page = self.next_link.format(self.page)
        self.page += 1

        news_links = []
        try:
            news_div = response.xpath("//div[@class='w685 fl']")
        except:
            self.log(response.request.url)
            news_div = None

        if news_div == None:
            return

        # extract highlight news
        try:
            highlight_box = news_div.xpath(".//div[@class='box-focus']")[0]
            # top 1 news
            top1_news = highlight_box.xpath(".//div[contains(@class, 'top1')]/a[@class='img375x250']")[0]
            news_links.append(self.root_url + top1_news.xpath("@href").get())
            # top 2 news
            # top2_news = highlight_box.xpath(".//div[contains(@class,'listtop2')]")[0]
            # for news in top2_news.xpath(".//ul[@class='list-item']/li[@class='item'][@data-boxtype='zonenewsposition']"):
            #     link = news.xpath(".//a[@data-linktype='newsdetail']/@href").get()
            #     news_links.append(self.root_url + link)
        except Exception as ex:
            self.log("There is no hightlight news" + str(ex), level=logging.ERROR)
            pass

        # extract normal news
        for entry in news_div.xpath(".//div[@class='news-stream']"):
            links = entry.xpath(".//ul[@class='listnews']/li/a/@href").getall()
            links = ["".join([self.root_url, x]) for x in links]
            news_links.extend(links)

        if len(news_links) != 0:
            yield Request(
                url=next_page,
                callback=self.parse_list_page
            )

        for news_link in news_links:
            yield Request(
                url=news_link,
                callback=self.extract_news
            )

    def extract_news(self, response):
        """Function to extract content of new from html

        :param response: raw data of a news page
        
        """
        if self.limit > 0 and self.num_news > self.limit:
            return
        self.num_news += 1
        item = NewsLoader(item=NewsItems(), response=response, date_fmt=["%H:%M | %d/%m/%Y"],
                          date_regex="((\d{2}):(\d{2}) \| (\d{1,2})/(\d{1,2})/(\d{4}))")
        entry = response.xpath("//div[contains(@class, 'vnb-body')]")[0]
        title = entry.xpath(".//h1[@class='vnbcb-title']/text()").get().strip()
        created_date = entry.xpath(".//span[@class='vnbcbat-data ']/text()").get().strip()
        source_url = response.request.url
        brief_content = "".join(entry.xpath(".//div[@class='vnbcbc-sapo']/descendant::text()").getall()).strip()
        main_content = ""
        for p in entry.xpath(".//div[@id='vnb-detail-content']/p"):
            main_content = "\n".join([main_content, "".join(p.xpath("./descendant::text()").getall()).strip()])
            # "\n".join(entry.xpath(".//div[@id='vnb-detail-content']/p/descendant::text()").getall())
        category = self.group

        item.add_value("title", title)
        item.add_value("published_date", item.find_published_date(created_date))
        item.add_value("source_url", source_url)
        item.add_value("brief_content", brief_content)
        item.add_value("content", main_content)
        item.add_value("category", category)
        item.add_value("site", "https://vietnambiz.vn")

        from datetime import datetime
        import pytz
        today = datetime.now(pytz.timezone('Asia/Bangkok')).replace(tzinfo=None)
        item.add_value("created_at", today)

        yield item.load_item()
