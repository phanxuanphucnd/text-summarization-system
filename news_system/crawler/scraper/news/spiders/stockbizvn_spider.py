# -*- coding: utf-8 -*-

import scrapy
import datetime
from scrapy.http import Request
import dateutil.parser as dparser
from news.items import NewsItems
from news.loader import NewsLoader
import re

from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
import pytz


class Stockbizvn(scrapy.Spider):
    name = "stockbizvn"
    # allowed_domains = ["www.stockbiz.vn"]

    # scrapy crawl stockbizvn -a group=banking_group
    # -a start_url=https://www.stockbiz.vn/Stocks/VPB/CompanyNews.aspx \

    # ALL URLS:
    #     "https://www.stockbiz.vn/Stocks/VPB/CompanyNews.aspx",
    #     "https://www.stockbiz.vn/Stocks/ACB/CompanyNews.aspx",
    #     "https://www.stockbiz.vn/Stocks/MBB/CompanyNews.aspx",
    #     "https://www.stockbiz.vn/Stocks/HDB/CompanyNews.aspx",
    #     "https://www.stockbiz.vn/Stocks/EIB/CompanyNews.aspx",
    #     "https://www.stockbiz.vn/Stocks/VCB/CompanyNews.aspx"
    # ]

    num_news = 0
    limit = -1

    driver_path = './drivers/chromedriver'
    chromeOptions = Options()
    chromeOptions.headless = True
    chromeOptions.add_argument('--disable-dev-shm-usage')

    def __init__(self, category="", **kwargs):
        super().__init__(**kwargs)

        if self.limit != -1:
            self.limit = int(self.limit)

        self.main_driver = webdriver.Chrome(executable_path=self.driver_path,
                                            options=self.chromeOptions,
                                            service_log_path='NUL')

        self.force_stop = False

    def start_requests(self):
        yield Request(url=self.start_url, callback=self.parse)

    def parse(self, response):
        """ This spider would start with page, collecting category links, and item links, 
        parsing the latter with this function method

        :param response: response of the start page

        """

        self.main_driver.implicitly_wait(5)
        self.main_driver.get(response.url)

        # yield Request(url=self.start_url, callback=self.parse_content_table)

        check = True

        entries = self.main_driver.find_elements_by_css_selector('.news_title a')
        news_links = [entry.get_attribute('href') for entry in entries]

        for news_link in news_links:
            if self.limit > 0 and self.num_news > self.limit:
                check = False
                return
            else:
                yield Request(url=news_link, callback=self.parse_content)
        #sleep(5)
        '''
        while check == True and self.force_stop == False:
            news_links = []
            btn_next = None

            try:
                try:
                    # self.main_driver.implicitly_wait(10)

                    btn_next = self.main_driver.find_elements_by_xpath(
                        '//div[@class="pageNavigation"]//*')[-1]
                    self.main_driver.implicitly_wait(5)
                    ActionChains(self.main_driver).move_to_element(btn_next).click(btn_next).perform()
                except Exception as e:
                    print("Button next-page not existed ! ", e)
                    check = False
                    break

                self.main_driver.implicitly_wait(5)
                sleep(5)
                entries = self.main_driver.find_elements_by_css_selector('.news_title a')
                news_links = [entry.get_attribute('href') for entry in entries]

                if len(news_links) == 0:
                    break

                for news_link in news_links:
                    if self.limit > 0 and self.num_news > self.limit:
                        check = False
                        return
                    else:
                        yield Request(url=news_link, callback=self.parse_content)
            except Exception as e:
                print(f"ERROR: {e}")
        '''
        self.main_driver.close()

    def date_parse(self, text):

        date_parse = dparser.parse(text, fuzzy=True)
        date_fmt = "%d/%m/%Y - %H:%M:%S"
        if "SA" in text:
            str_date = date_parse.strftime(date_fmt) + " AM"
        elif "CH" in text:
            str_date = date_parse.strftime(date_fmt) + " PM"

        tmp = datetime.datetime.strptime(str_date, '%d/%m/%Y - %I:%M:%S %p')

        return tmp.strftime(date_fmt)

    def parse_content_table(self, response):
        """Function to extract content of new from html

        :param response: raw data of a news page
        
        """

        # item = NewsLoader(item=NewsItems(), response=response, date_fmt=["%d-%m-%Y - %H:%M:%S"])
        item = NewsLoader(item=NewsItems(), response=response, date_fmt=["%d/%m/%Y %H:%M:%S %p"],
                          date_regex="((\d{2})/(\d{2})/(\d{4}) (\d{2}):(\d{2}):(\d{2}) (AM|PM))")

        category = self.group
        source_url = response.request.url
        title = response.xpath('//*[@class="stockName"]/text()').get().strip()
        date = response.xpath('//*[@id="headerQuoteContainerLarge"]/div[2]/div/span[1]/text()').get()
        time = response.xpath('//*[@id="headerQuoteContainerLarge"]/div[2]/div/span[2]/span/text()').get()
        published_date = self.date_parse(date.strip() + " - " + time.strip())
        published_date = re.sub(r'CH', 'PM', published_date)
        published_date = re.sub(r'SA', 'AM', published_date)
        brief_content = title

        content = response.css('[id="headerQuoteContainerLarge"] ::text').extract()
        content = "\n".join(nd.strip() for nd in content)

        item.add_value('title', title)
        item.add_value('category', category)
        item.add_value('source_url', source_url)
        item.add_value('published_date', published_date)
        item.add_value('brief_content', brief_content.strip())
        item.add_value('content', content)
        item.add_value('site', 'https://www.stockbiz.vn')
        item.add_value('stock_code', self.stock_code)

        yield item.load_item()

    def parse_content(self, response):

        if self.limit > 0 and self.num_news > self.limit:
            return
        self.num_news += 1

        item = NewsLoader(item=NewsItems(), response=response, date_fmt=["%d/%m/%Y %H:%M:%S %p"],
                          date_regex="((\d{2})/(\d{2})/(\d{4}) (\d{2}):(\d{2}):(\d{2}) (AM|PM))")

        category = self.group
        source_url = response.request.url
        title = response.xpath('//*[@class="news_title"]/text()').get().strip()
        published_date = response.xpath('//*[@class="news_date"]/text()').get()
        published_date = re.sub('CH', 'PM', published_date)
        published_date = re.sub('SA', 'AM', published_date)
        brief_content = ""
        content = ""

        check = True

        for div in response.xpath("//span[@class='news_content']/p"):
            if div.xpath("./strong") and check:
                brief_content = "\n".join([brief_content, "".join(div.xpath("./descendant::text()").getall()).strip()])
            else:
                content = "\n".join([content, "".join(div.xpath("./descendant::text()").getall()).strip()])
                check = False
        check = True
        for div in response.xpath("//span[@class='news_content']/div"):
            if div.xpath("./strong") and check:
                brief_content = "\n".join([brief_content, "".join(div.xpath("./descendant::text()").getall()).strip()])
            else:
                content = "\n".join([content, "".join(div.xpath("./descendant::text()").getall()).strip()])
                check = False
        brief_content = brief_content.strip()
        content = content.strip()
        if len(brief_content) == 0:
            brief_content = content
        # content = response.css('.news_content ::text').extract()
        # content = "\n".join(nd.strip() for nd in content)
        try:
            attachment_url = response.xpath(
                '//*[@id="ctl00_webPartManager_wp801213449_wp849033637_lnkAttachedFile"]/@href').getall()

        except:
            attachment_url = None

        if attachment_url:
            attachment_url = ["".join(["https://www.stockbiz.vn", x.strip()]) for x in attachment_url]
            brief_content = brief_content.strip() + "\n" + '\n'.join(attachment_url)
            content = content.strip() + "\n" + '\n'.join(attachment_url)

        item.add_value('title', title)
        item.add_value('category', category)
        item.add_value('source_url', source_url)
        item.add_value('published_date', published_date)
        item.add_value('brief_content', brief_content.strip())
        item.add_value('content', content)
        item.add_value("site", "https://www.stockbiz.vn")
        item.add_value("stock_code", self.stock_code)

        from datetime import datetime

        today = datetime.now(pytz.timezone('Asia/Bangkok')).replace(tzinfo=None)
        item.add_value("created_at", today)

        # item.add_value("title", title)
        # item.add_value("published_date", published_date)
        # item.add_value("source_url", source_url)
        # item.add_value("brief_content", brief_content)
        # item.add_value("content", content)
        # item.add_value("category", category)

        # yield item.load_item()

        if title.find(":") >= 0:
            check_stock_code = title[:title.find(":")]
        else:
            check_stock_code = ""
        if len(check_stock_code) > 0:
            if check_stock_code.strip() == self.stock_code:
                yield item.load_item()
        else:
            yield item.load_item()
