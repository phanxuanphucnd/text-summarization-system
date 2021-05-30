# -*- coding: utf-8 -*-

from scrapy import Spider
from scrapy.http import Request
from news.items import NewsItems
from news.loader import NewsLoader
import requests

from time import sleep

'''
Spider class for crawl pages
'''

import json

class ndhSpider(Spider):
    # Crawling CafeF example
    name = 'ndh'

    # scrapy crawl ndh -a group=khoi_ngan_hang -a start_url=https://ndh.vn/tai-chinh \
    # -a root_url=https://ndh.vn -a next_link="https://ndh.vn/lazyload-more?data={\"page\":{0},\"cate_id\":\"1000596\"}"

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

        news_links = []

        entry = response.xpath("//div[@id='content-folder']")[0]

        # extract feature news
        news_links.append(entry.xpath(".//article[@class='featured-news']").xpath(".//h1[@class='title-news']/a/@href").get())

        # extract top news
        news_links.extend(entry.xpath(".//div[@class='list-large-thumb']/article/h3[@class='title-news']/a/@href").getall())

        # extract normal news
        news_links.extend(entry.xpath(".//div[@class='list-news']/article/div[@class='content']/h3/a/@href").getall())

        # normalize news links
        news_links = ["".join([self.root_url, x]) for x in news_links]

        # print("===>", news_links)

        for news_link in news_links:
            yield Request(
                url=news_link,
                callback=self.extract_news
            )

        '''
        self.crr_list_news = ''
        #sleep(3)
        while True and self.force_stop == False and self.page < 100:
            #news_links = []
            next_page = self.next_link.format(self.page)
            
            yield Request(url=next_page, callback=self.get_next_page)#, headers={'Cache-Control': 'no-cache'}, proxies= {"http": "165.227.186.129:80"})
            #if r.text == crr_list_news:
            #    print(r.text)
            #    break
            #crr_list_news = r.text
            #news_list = r.json()['data']
            #for news in news_list:
            #    news_links.append("".join([self.root_url, news['share_url']]))

            #for news_link in news_links:
            #    yield Request(
            #        url=news_link,
            #        callback=self.extract_news
            #    )
            self.page += 1
            #sleep(5)
            sleep(3)
            print(self.force_stop)
        '''

    def get_next_page(self, response):
        if response.text == self.crr_list_news:
            self.force_stop = True
        self.crr_list_news = response.text
        r = json.loads(response.text)
        news_list = r['data']
        news_links = []
        for news in news_list:
            news_links.append("".join([self.root_url, news['share_url']]))

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
        item = NewsLoader(item=NewsItems(), response=response, date_fmt=["%d/%m/%Y, %H:%M"],
                          date_regex="((\d{1,2})/(\d{1,2})/(\d{4}), (\d{2}):(\d{2}))")
        try:
            entry = response.xpath("//section[@class='section container detail-pages']/div[@class='main-content']")[0]
            title = entry.xpath(".//h1[@class='title-detail']/text()").get().strip()
            created_date = entry.xpath(".//span[@class='date-post']/text()").get().strip()
            source_url = response.request.url
            brief_content = entry.xpath(".//p[@class='related-news']/text()").get().strip()
            if len(brief_content) == 0:
                brief_content = "".join(entry.xpath(".//p[@class='related-news']/a/text()").getall()).strip()
            main_content = ""
            for p in entry.xpath(".//article[@class='fck_detail']/p"):
                main_content = main_content + "\n" + "".join(p.xpath("./descendant::text()").getall()).strip()
            category = self.group

            item.add_value("title", title)
            item.add_value("published_date", item.find_published_date(created_date))
            item.add_value("source_url", source_url)
            item.add_value("brief_content", brief_content)
            item.add_value("content", main_content)
            item.add_value("category", category)
            item.add_value("site", "https://ndh.vn")

            from datetime import datetime
            import pytz
            today = datetime.now(pytz.timezone('Asia/Bangkok')).replace(tzinfo=None)
            item.add_value("created_at", today)

            self.num_news += 1
            yield item.load_item()
        except:
            pass
