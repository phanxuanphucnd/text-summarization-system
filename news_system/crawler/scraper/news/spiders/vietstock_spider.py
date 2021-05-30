# -*- coding: utf-8 -*-

from scrapy import Spider
from scrapy.http import Request
from news.items import NewsItems
from news.loader import NewsLoader

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
from datetime import datetime, timedelta

from time import sleep
from pyvirtualdisplay import Display
import pytz

LOGGER.setLevel(logging.ERROR)

'''
Spider class for crawl pages
'''


class VietstockSpider(Spider):
    # Crawling Tinnhanhchungkhoan class
    name = 'Vietstock'

    # scrapy crawl Vietstock -a group=stock_market \
    # -a start_url=https://vietstock.vn/doanh-nghiep/hoat-dong-kinh-doanh.htm -a root_url=https://vietstock.vn

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
        # self.num_news += 1
        self.main_driver.get(response.url)

        news_links = []

        # timeline news
        for entry in self.main_driver.find_elements_by_xpath(
                "//div[@id='channel-container']/section"):
            news_links.append(entry.find_element_by_xpath(".//div[@class='thumb']/a").get_attribute('href'))

        for news_link in news_links:
            yield Request(
                url=news_link,
                callback=self.extract_news
            )

        self.no_pages = 0

        while True and self.force_stop == False:
            news_links = []
            next = self.main_driver.find_element_by_xpath("//li[@id='page-next ']/a")
            try:
                next.click()
                self.main_driver.implicitly_wait(3)
                sleep(3)
                # timeline news
                for entry in self.main_driver.find_elements_by_class_name("channel-title"):
                    news_links.append(entry.find_element_by_tag_name('a').get_attribute('href'))
                    # sleep(0.5)
                self.no_pages += 1
                if len(news_links) == 0:
                    break

                for news_link in news_links:
                    yield Request(
                        url=news_link,
                        callback=self.extract_news
                    )

            except Exception as ex:
                print("error:", ex)
                # print("--->", news_links)
                break

        self.main_driver.close()
        self.display.stop()

    def extract_news(self, response):
        """Function to extract content of new from html

        :param response: raw data of a news page
        
        """
        self.num_news += 1
        if self.limit > 0 and self.num_news > self.limit:
            self.force_stop = True
            return

        item = NewsLoader(item=NewsItems(), response=response, date_fmt=["%d/%m/%Y %H:%M"],
                          date_regex="((\d{1,2})/(\d{1,2})/(\d{4}) (\d{2}):(\d{2}))")

        try:
            entry = response.xpath("//div[@class='blog-excerpt ']")
            title = entry.xpath(".//div[@class='blog-single-head']/h1/text()").get().strip()
            created_date = entry.xpath(".//div[@class='blog-single-head']").xpath(
                ".//span[@class='date']/text()").get().strip()
            source_url = response.request.url
            brief_content = title
            try:
                brief_content = "".join(
                    entry.xpath(".//p[contains(@class, 'pHead')]/descendant::text()").getall()).strip()
                if len(brief_content) == 0:
                    brief_content = title
            except:
                pass
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

            # pre-process date
            if "giờ trước" in created_date:
                delta = int(created_date[:created_date.find(' ')])
                valid_date_time = datetime.now(pytz.timezone('Asia/Bangkok')) - timedelta(hours=delta)
                created_date = valid_date_time.strftime("%d/%m/%Y %H:%M")

            try:
                attachment = "\n".join(
                    entry.xpath(".//table[@style='border-collapse:collapse;']/tbody/tr/td/a/@href").getall())
                brief_content = "\n".join([brief_content, attachment])
            except Exception as ex:
                print(ex)
                pass
            item.add_value("title", title)
            item.add_value("published_date", item.find_published_date(created_date))
            item.add_value("source_url", source_url)
            item.add_value("brief_content", brief_content)
            item.add_value("content", main_content)
            item.add_value("category", category)
            item.add_value("site", "https://vietstock.vn")

            import pytz
            today = datetime.now(pytz.timezone('Asia/Bangkok')).replace(tzinfo=None)
            item.add_value("created_at", today)

            yield item.load_item()
        except:
            title = response.xpath(".//h1[@class='hTitle']/text()").get().strip()
            created_date = None
            try:
                created_date = response.xpath(".//p[@class='blog-single-head']").xpath(
                    ".//span[@class='date']/text()").get().strip()
            except:
                pass

            source_url = response.request.url
            main_content = ""
            brief_content = title
            try:
                brief_content = "".join(
                    response.xpath(".//p[contains(@class, 'pHead')]/descendant::text()").getall()).strip()
                if len(brief_content) == 0:
                    brief_content = title
            except:
                pass

            try:
                for p in entry.xpath(".//p"):
                    main_content = main_content + "\n" + "".join(p.xpath("./descendant::text()").getall()).strip()
                main_content = main_content.strip()
            except:
                pass
            if len(main_content) == 0:
                main_content = brief_content
            category = self.group
            try:
                attachment = "\n".join(
                    response.xpath("//table[@style='border-collapse:collapse;']/tbody/tr/td/a/@href").getall())
                brief_content = "\n".join([brief_content, attachment])
            except Exception as ex:
                print(ex)
                pass

            item.add_value("title", title)
            item.add_value("published_date", created_date)
            item.add_value("source_url", source_url)
            item.add_value("brief_content", brief_content)
            item.add_value("content", main_content)
            item.add_value("category", category)
            item.add_value("site", "https://vietstock.vn")


            import pytz
            today = datetime.now(pytz.timezone('Asia/Bangkok')).replace(tzinfo=None)
            item.add_value("created_at", today)

            yield item.load_item()
