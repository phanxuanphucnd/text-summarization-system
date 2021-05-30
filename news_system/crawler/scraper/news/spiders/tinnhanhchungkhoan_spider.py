# -*- coding: utf-8 -*-
import pytz as pytz
from scrapy import Spider
from scrapy.http import Request
from news.items import NewsItems
from news.loader import NewsLoader

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging
from selenium.webdriver.remote.remote_connection import LOGGER

from datetime import datetime, timedelta
import pytz

from pyvirtualdisplay import Display

LOGGER.setLevel(logging.ERROR)

'''
Spider class for crawl pages
'''


class TinnhanhchungkhoanSpider(Spider):
    # Crawling Tinnhanhchungkhoan class
    name = 'Tinnhanhchungkhoan'

    # scrapy crawl Tinnhanhchungkhoan -a group=macro \
    # -a start_url=https://tinnhanhchungkhoan.vn/dau-tu/ -a root_url=https://tinnhanhchungkhoan.vn

    # don't show web browser
    chromeOptions = Options()
    chromeOptions.headless = True
    chromeOptions.add_argument('--no-sandbox')
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

        if self.limit > 0 and self.num_news > self.limit and self.force_stop:
            return
        # self.num_news += 1
        self.main_driver.get(response.url)

        news_links = []

        # rank 1 news
        news_links.append(self.main_driver.find_element_by_xpath("//div[@class='rank-1']").find_element_by_xpath(
            ".//h2[@class='story__heading']/a").get_attribute('href'))

        # rank 2 news
        rank2_news = self.main_driver.find_elements_by_xpath("//div[@class='rank-2']/article")
        for entry in rank2_news:
            news_links.append(entry.find_element_by_xpath(".//h2[@class='story__heading']/a").get_attribute('href'))

        # timeline news
        for entry in self.main_driver.find_elements_by_xpath(
                "//div[@class='category-timeline']/div[@class='box-content']"):
            news_links.append(entry.find_element_by_xpath(".//h2[@class='story__heading']/a").get_attribute('href'))

        for news_link in news_links:
            yield Request(
                url=news_link,
                callback=self.extract_news
            )

        while True and self.force_stop == False:
            news_links = []
            refresh_command = "var element = document.getElementsByClassName('category-timeline')[" \
                              "0].firstElementChild; element.innerHTML = '';"
            self.main_driver.execute_script(refresh_command)
            next = self.main_driver.find_element_by_xpath("//button[@id='viewmore'][@type='button'][text()='Xem thêm']")
            try:
                next.click()
                self.main_driver.implicitly_wait(3)
                # timeline news
                for entry in self.main_driver.find_element_by_class_name(
                        "category-timeline").find_elements_by_class_name("story__heading"):
                    news_links.append(
                        entry.find_element_by_tag_name('a').get_attribute('href'))

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
        item = NewsLoader(item=NewsItems(), response=response, date_fmt=["%d/%m/%Y %H:%M"],
                          date_regex="((\d{1,2})/(\d{1,2})/(\d{4}) (\d{2}):(\d{2}))")
        entry = response.xpath("//div[@class='main-column article']")[0]
        title = entry.xpath(".//h1[@class='article__header cms-title']/text()").get().strip()
        created_date = entry.xpath(".//div[@class='article__meta']/time/text()").get().strip()
        source_url = response.request.url
        try:
            brief_content = "".join(entry.xpath(".//div[@class='article__sapo cms-desc']/descendant::text()").getall()).strip()
        except:
            brief_content = "".join(entry.xpath(".//div[@class='article__sapo cms-desc']/div/descendant::text()").getall()).strip()
        if len(brief_content) == 0:
            brief_content = title
        main_content = ""
        for p in entry.xpath(".//div[@class='article__body cms-body']/p"):
            main_content = main_content + "\n" + "".join(p.xpath("./descendant::text()").getall()).strip()
        if len(main_content) == 0:
            main_content = brief_content
        category = self.group

        # pre-process date
        if "giờ trước" in created_date:
            delta = int(created_date[:created_date.find(' ')])
            valid_date_time = datetime.now(pytz.timezone('Asia/Bangkok')) - timedelta(hours=delta)
            created_date = valid_date_time.strftime("%d/%m/%Y %H:%M")

        item.add_value("title", title)
        item.add_value("published_date", item.find_published_date(created_date))
        item.add_value("source_url", source_url)
        item.add_value("brief_content", brief_content)
        item.add_value("content", main_content)
        item.add_value("category", category)
        item.add_value("site", "https://tinnhanhchungkhoan.vn")

        import pytz
        today = datetime.now(pytz.timezone('Asia/Bangkok')).replace(tzinfo=None)
        item.add_value("created_at", today)

        yield item.load_item()
