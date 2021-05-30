# -*- coding: utf-8 -*-

import scrapy
from scrapy.http import Request
from news.items import NewsItems
from news.loader import NewsLoader

from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging
from selenium.webdriver.remote.remote_connection import LOGGER

LOGGER.setLevel(logging.ERROR)
from time import sleep
from datetime import datetime, timedelta
import pytz

class FinanceVietstock(scrapy.Spider):
    name = "financevietstock"
    # allowed_domains = ["finance.vietstock.vn"]

    # GROUP_MAPPING_RULES = {
    #     'TCB': 'banking_group',
    #     'STB': 'banking_group',
    #     'ROS': 'real_estate',
    #     'FLC': 'real_estate',
    #     'VIC': 'vin',
    #     'VRE': 'vin',
    #     'VHM': 'vin'
    # }

    # scrapy crawl financevietstock -a group=banking_group
    # -a start_url="https://finance.vietstock.vn/TCB/tin-tuc-su-kien.htm"

    # start_urls = [
    #     "https://finance.vietstock.vn/TCB/tin-tuc-su-kien.htm",
    #     "https://finance.vietstock.vn/STB/tin-tuc-su-kien.htm",
    #     "https://finance.vietstock.vn/ROS/tin-tuc-su-kien.htm",
    #     "https://finance.vietstock.vn/FLC/tin-tuc-su-kien.htm",
    #     "https://finance.vietstock.vn/VIC/tin-tuc-su-kien.htm",
    #     "https://finance.vietstock.vn/VRE/tin-tuc-su-kien.htm",
    #     "https://finance.vietstock.vn/VHM/tin-tuc-su-kien.htm",
    # ]

    num_news = 0
    limit = -1

    driver_path = './drivers/chromedriver'
    chromeOptions = Options()
    chromeOptions.headless = True
    chromeOptions.add_argument('--no-sandbox')
    force_stop = False

    def __init__(self, category="", **kwargs):
        super().__init__(**kwargs)

        if self.limit != -1:
            self.limit = int(self.limit)

        self.main_driver = webdriver.Chrome(executable_path=self.driver_path,
                                            options=self.chromeOptions,
                                            service_log_path='NUL')

    def start_requests(self):
        yield Request(url=self.start_url, callback=self.parse)

    def parse(self, response):
        """ This spider would start with page, collecting category links, and item links, 
        parsing the latter with this function method

        :param response: response of the start page

        """

        self.main_driver.get(response.url)
        self.main_driver.implicitly_wait(3)

        news_links = []

        entries_left = self.main_driver.find_elements_by_css_selector(
            '.pos-relative .table-responsive.clear-fix.pos-relative .text-link')
        for entry in entries_left:
            value = entry.get_attribute('href')
            if value not in news_links:
                news_links.append(value)

        # entries_right = self.main_driver.find_elements_by_css_selector(
        #     ".table.table-striped.table-middle.pos-relative .text-link")
        # for entry in entries_right:
        #     value = entry.get_attribute('href')
        #     if value not in news_links:
        #         news_links.append(value)

        for news_link in news_links:
            if news_link:
                yield Request(url=news_link, callback=self.parse_content)
        check = True
        '''
        while check == True and self.force_stop == False:
            try:
                # self.main_driver.implicitly_wait(3)
                news_link = []
                btn_nexts = self.main_driver.find_elements_by_css_selector('.pos-relative .table-responsive.clear-fix.pos-relative .fa.fa-chevron-left')
                force_stop = True
                # print(btn_next)
                # for btn_next in btn_nexts:
                try:
                    for btn_next in btn_nexts:
                        try:
                            btn_next.click()
                            self.main_driver.implicitly_wait(3)
                            force_stop = False
                        except:
                            pass
                    if force_stop:
                        break
                    sleep(3)

                    entries_left = self.main_driver.find_elements_by_css_selector(
                        '.pos-relative .table-responsive.clear-fix.pos-relative .text-link')
                    for entry in entries_left:
                        value = entry.get_attribute('href')
                        if value not in news_links:
                            if self.limit > 0 and len(news_links) > self.limit:
                                check = False
                                break
                            else:
                                news_links.append(value)

                    # entries_right = self.main_driver.find_elements_by_css_selector(
                    #     ".table.table-striped.table-middle.pos-relative .text-link")
                    # for entry in entries_right:
                    #     value = entry.get_attribute('href')
                    #     if value not in news_links:
                    #         if self.limit > 0 and len(news_links) > self.limit:
                    #             check = False
                    #             break
                    #         else:
                    #             news_links.append(value)
                except:
                    print(f"{btn_next} not clickable")
                    break


                if len(news_links) > self.limit and self.limit > 0:
                    break


            except Exception as ex:
                print("Button next-page not existed !")
                print(ex)
                break

            print("LENGTH TOTAL LINKS: ", len(news_links))

            for news_link in news_links:
                if news_link:
                    yield Request(url=news_link, callback=self.parse_content)
        '''
        self.main_driver.close()

    def parse_content(self, response):
        """Function to extract content of new from html

        :param response: raw data of a news page
        
        """

        # item = NewsLoader(item=NewsItems(), response=response)
        # item = NewsLoader(item=NewsItems(), response=response, date_fmt=["%d/%m/%Y %H:%M"],
        #                   date_regex="((\d{2})/(\d{2})/(\d{4}) (\d{2}):(\d{2})")

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
                brief_content = "".join(entry.xpath(".//p[contains(@class, 'pHead')]/descendant::text()").getall()).strip()
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
                attachment = "\n".join(entry.xpath(".//table[@style='border-collapse:collapse;']/tbody/tr/td/a/@href").getall())
                brief_content = "\n".join([brief_content, attachment])

                main_content = main_content.strip() + "\n" + attachment
            except Exception as ex:
                print(ex)
                pass
            item.add_value("title", title)
            item.add_value("published_date", item.find_published_date(created_date))
            item.add_value("source_url", source_url)
            item.add_value("brief_content", brief_content)
            item.add_value("content", main_content)
            item.add_value("category", category)
            item.add_value("site", "https://finance.vietstock.vn")
            item.add_value("stock_code", self.stock_code)

            today = datetime.now(pytz.timezone('Asia/Bangkok')).replace(tzinfo=None)
            item.add_value("created_at", today)

            if title.find(":") >= 0:
                check_stock_code = title[:title.find(":")]
            else:
                check_stock_code = ""
            if len(check_stock_code) > 0:
                if check_stock_code.strip() == self.stock_code:
                    yield item.load_item()
            else:
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
                brief_content = "".join(response.xpath(".//p[contains(@class, 'pHead')]/descendant::text()").getall()).strip()
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
                attachment = "\n".join(response.xpath("//table[@style='border-collapse:collapse;']/tbody/tr/td/a/@href").getall())
                brief_content = "\n".join([brief_content, attachment])
                main_content = main_content.strip() + "\n" + attachment
            except Exception as ex:
                print(ex)
                pass

            item.add_value("title", title)
            item.add_value("published_date", created_date)
            item.add_value("source_url", source_url)
            item.add_value("brief_content", brief_content)
            item.add_value("content", main_content)
            item.add_value("category", category)
            item.add_value("site", "https://finance.vietstock.vn")
            item.add_value("stock_code", self.stock_code)

            today = datetime.now(pytz.timezone('Asia/Bangkok')).replace(tzinfo=None)
            item.add_value("created_at", today)

            if title.find(":") >= 0:
                check_stock_code = title[:title.find(":")]
            else:
                check_stock_code = ""
            if len(check_stock_code) > 0:
                if check_stock_code.strip() == self.stock_code:
                    yield item.load_item()
            else:
                yield item.load_item()
