# -*- coding: utf-8 -*-

import time
from scrapy import Spider
from scrapy import Request
from news.items import NewsItems
from news.loader import NewsLoader
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException        
from selenium.common.exceptions import ElementClickInterceptedException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging
from selenium.webdriver.remote.remote_connection import LOGGER

from pyvirtualdisplay import Display

LOGGER.setLevel(logging.ERROR)


class VingroupSpider(Spider):
    """VinGroup. """

    name = "vingroup"
    allowed_domains = ["vingroup.net"]

    start_url = "https://vingroup.net/tin-tuc-su-kien"
        
    group = 'vin'

    driver_path = './drivers/chromedriver'

    count = 0
    limit = -1
    
    chromeOptions = Options()
    chromeOptions.headless = True
    chromeOptions.add_argument('--no-sandbox')
    
    def __init__(self, category='', **kwargs):
        super().__init__(**kwargs)
        if self.limit != -1:
            self.limit = int(self.limit)
        self.force_stop = False
        
        self.main_driver = webdriver.Chrome(executable_path=self.driver_path, 
                                            options=self.chromeOptions, 
                                            service_log_path='NUL')
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()

    def start_requests(self):
        yield Request(url=self.start_url, callback=self.parse)

    def parse(self, response):
        """ This spider would start with page, collecting category links, and item links, 
        parsing the latter with this function method

        :param response: response of the start page

        """

        self.main_driver.implicitly_wait(5)
        self.main_driver.get(response.url)

        entries = self.main_driver.find_elements_by_css_selector('.itemNews .link')

        news_links = [entry.get_attribute('href') for entry in entries]
        

        print(f'\nNews links: {len(news_links)} {news_links} \n')

        for news_link in news_links:
            if (self.limit > 0 and self.count > self.limit) or self.force_stop:
                return
            else:
                yield Request(url=news_link, callback=self.parse_content)

        while True and self.force_stop == False:
            try:
                self.main_driver.implicitly_wait(5)
                btn_next = self.main_driver.find_element_by_xpath('//*[@class="fas fa-chevron-right"]')
                btn_next.click()
            except NoSuchElementException:
                print("Button next-page not existed !")
                break


            self.main_driver.implicitly_wait(5)
            entries = self.main_driver.find_elements_by_css_selector('.itemNews .link')
            news_links = [entry.get_attribute('href') for entry in entries]

            print(f'\nNews links: {len(news_links)} {news_links} \n')

            if len(news_links) == 0:
                break

            for news_link in news_links:
                if (self.limit > 0 and self.count > self.limit) or self.force_stop:
                    return  
                else:
                    yield Request(url=news_link, callback=self.parse_content)
        
        self.main_driver.close()
        self.display.stop()


    def parse_content(self, response):
        """Function to extract content of new from html

        :param response: raw data of a news page
        
        """

        # item = NewsLoader(item=NewsItems(), response=response, date_fmt=["%m/%d/%y"])
        if self.limit > 0 and self.count > self.limit:
            return
        self.count += 1

        item = NewsLoader(item=NewsItems(), response=response, date_fmt=["%d-%m-%Y"],
                          date_regex="((\d{1,2})-(\d{1,2})-(\d{4})")

        title = response.css('.container .infoNews > h2::text').get().strip()
        category = self.group
        source_url = response.request.url
        published_date = response.css('.infoNews > p::text').get().strip()
        brief_content = title
        content = response.css('.content ::text').getall()

        item.add_value('title', title)
        item.add_value('category', category)
        item.add_value('source_url', source_url)
        item.add_value('published_date', published_date)
        item.add_value('brief_content', brief_content)
        item.add_value('content', "\n".join(nd.strip() for nd in content))
        item.add_value("site", "https://vingroup.net")

        from datetime import datetime
        import pytz
        today = datetime.now(pytz.timezone('Asia/Bangkok')).replace(tzinfo=None)
        item.add_value("created_at", today)

        # from pprint import pprint
        # print('\n')
        # pprint(item)

        # item.add_value("title", title)
        # item.add_value("created_date", created_date)
        # item.add_value("source_url", source_url)
        # item.add_value("brief_content", brief_content)
        # item.add_value("content", content)
        # item.add_value("category", category)

        # yield item.load_item()

        yield item.load_item()