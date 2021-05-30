# -*- coding: utf-8 -*-

from scrapy import Spider
from scrapy.http import Request
from news.items import NewsItems
from news.loader import NewsLoader

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging
from selenium.webdriver.remote.remote_connection import LOGGER

from pyvirtualdisplay import Display

LOGGER.setLevel(logging.ERROR)

'''
Spider class for crawl pages
'''


class BIDVSpider(Spider):
    # Crawling Tinnhanhchungkhoan class
    name = 'BIDV'

    # scrapy crawl BIDV -a group=banking \
    # -a start_url=https://www.bidv.com.vn/vn/ve-bidv/tin-tuc/tin-ve-bidv -a root_url=https://www.bidv.com.vn

    # don't show web browser
    chromeOptions = Options()
    chromeOptions.headless = True

    num_news = 0
    limit = -1

    def __init__(self, category='', **kwargs):
        super().__init__(**kwargs)
        if self.limit != -1:
            self.limit = int(self.limit)
        self.force_stop = False
        self.main_driver = webdriver.Chrome(executable_path="./drivers/chromedriver", options=self.chromeOptions,
                                            service_log_path='NUL')
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()

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
        self.main_driver.get(response.url)

        news_links = []

        # timeline news
        for entry in self.main_driver.find_elements_by_xpath(
                "//div[@class='news-list-items']/div[@class='thumbnail ng-scope']"):
            news_links.append(entry.find_element_by_xpath(".//a[@class='link-view-more']").get_attribute('href'))

        # print(news_links)

        for news_link in news_links:
            yield Request(
                url=news_link,
                callback=self.extract_news
            )

        while True and self.force_stop == False:
            news_links = []
            crr_page = self.main_driver.find_element_by_xpath(
                "//li[@class='active promotion-gold-page']/a").get_attribute('title')

            next = self.main_driver.find_element_by_xpath(
                "//li[@class='promotion-gold-page']/a[@title='{0}']".format(int(crr_page) + 1))
            try:
                next.click()
                self.main_driver.implicitly_wait(3)
                # timeline news
                for entry in self.main_driver.find_elements_by_xpath(
                        "//div[@class='news-list-items']/div[@class='thumbnail ng-scope']"):
                    news_links.append(
                        entry.find_element_by_xpath(".//a[@class='link-view-more']").get_attribute('href'))

                if len(news_links) == 0:
                    break

                for news_link in news_links:
                    yield Request(
                        url=news_link,
                        callback=self.extract_news
                    )

            except Exception as ex:
                print("error:", ex)
                break

        self.main_driver.close()
        self.display.stop()

    def extract_news(self, response):
        """Function to extract content of new from html

        :param response: raw data of a news page
        
        """
        if self.limit > 0 and self.num_news > self.limit:
            return
        self.num_news += 1
        item = NewsLoader(item=NewsItems(), response=response, date_fmt=["%d/%m/%Y"],
                          date_regex="((\d{2})/(\d{2})/(\d{4}))")

        entry = response.xpath("//div[@class='news-info']")
        title = response.xpath(".//h1[@class='title-1']/text()").get().strip()
        created_date = response.xpath(".//p[@class='published-date']/text()").get().strip()
        source_url = response.request.url
        brief_content = "".join(entry.xpath(".//i/descendant::text()").getall()).strip()
        main_content = ""
        for p in response.xpath(".//p"):
            main_content = "\n".join(main_content, "".join(p.xpath("./descendant::text()").getall()).strip())
        category = self.group

        item.add_value("title", title)
        item.add_value("published_date", item.find_published_date(created_date))
        item.add_value("source_url", source_url)
        item.add_value("brief_content", brief_content)
        item.add_value("content", main_content)
        item.add_value("category", category)
        item.add_value("site", "https://www.bidv.com.vn")

        from datetime import datetime
        import pytz
        today = datetime.now(pytz.timezone('Asia/Bangkok')).replace(tzinfo=None)
        item.add_value("created_at", today)
        
        yield item.load_item()
