# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy.http import Request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.remote_connection import LOGGER
from news.items import NewsItems
from news.loader import NewsLoader
# import logging

# LOGGER.setLevel(logging.ERROR)


class ForbesvietnamSpider(Spider):
    name = 'forbesvietnam'

    # scrapy crawl Forbesvietnam -a group=socialtrend -a start_url=https://forbesvietnam.com.vn/tin-cap-nhat/ -a root_url=https://forbesvietnam.com.vn -a number_page=50


    driver_path = './drivers/chromedriver'
    chromeOptions = Options()
    chromeOptions.headless = True
    chromeOptions.add_argument('--no-sandbox')

    # Instead of implementing a start_requests() method that generates scrapy.Request objects from URLs, you can just
    # define a start_urls class attribute with a list of URLs
    # def start_requests(self):
    #     for url in self.start_urls:
    #         yield Request(url = url, callback=self.parse)

    def __init__(self, category='', **kwargs):
        # super(ForbesvietnamSpider, self).__init__(**kwargs)
        # With python 3:
        super().__init__(**kwargs)
        self.main_driver = webdriver.Chrome(executable_path=self.driver_path,
                                            options=self.chromeOptions,
                                            service_log_path='NUL')

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

        page = response.url.split("/")
        print("--- We are processing : " + response.url)
        print("- Title: " + response.css('title::text').get())

        news_link = []

        list_links = response.xpath("//a[contains(@href, 'tin-cap-nhat/')]")
        # print("@@ 11111 @@: ", len(list_links))
        for link in list_links:
            sel = link.xpath("@href").get()
            if sel != u'/tin-cap-nhat' and sel != u'/tin-cap-nhat/' and not sel.startswith('/tin-cap-nhat/?trang='):
                abs_link = response.url + sel[1:]
                if abs_link not in news_link:
                    news_link.append(abs_link)
                    # print(abs_link)

        self.main_driver.get(response.url)

        loop = 0
        while True:
            loop += 1
            if loop == int(self.number_page):
                break
            next = self.main_driver.find_element_by_xpath("//a[@id='viewmore']")
            # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            try:
                next.click()
                self.main_driver.implicitly_wait(3)

                # print("@@ 11111 @@: ", len(self.main_driver.find_elements_by_xpath("//a[contains(@href,
                # 'tin-cap-nhat/')]")))
                for entry in self.main_driver.find_elements_by_xpath("//a[contains(@href, 'tin-cap-nhat/')]"):
                    # print("##" + entry.get_attribute('href') + "##")
                    abs_link = entry.get_attribute('href')
                    if abs_link not in news_link:
                        news_link.append(abs_link)
            except Exception as e:
                print("Exception: ", e)
                break

        for link in news_link:
            yield Request(url=link, callback=self.extract_news)

    def extract_news(self, response):
        """Function to extract content of new from html

        :param response: raw data of a news page
        
        """
        item = NewsLoader(item=NewsItems(), response=response, date_fmt=["%m/%d/%y"])

        try:
            title = response.xpath("//title/text()").get().strip()
            created_date = response.xpath("//li/a[contains(@href, 'javascript:voi(0);')]/text()").getall()[1]
            brief_content = response.xpath("//div[@class='sapo_detail cms-desc']/strong/p/text()").get()
            main_content = " ".join(response.xpath("//div[@class='cms-body']/p/text()").getall())
            source_url = response.request.url
            category = self.group
        except:
            return

        # print(title)

        item.add_value("title", title)
        item.add_value("published_date", created_date)
        item.add_value("source_url", source_url)
        item.add_value("summary", brief_content)
        item.add_value("content", main_content)
        item.add_value("category", category)
        item.add_value("site", "https://forbesvietnam.com.vn")
        item.add_value("stock_code", "---")

        from datetime import datetime
        import pytz
        today = datetime.now(pytz.timezone('Asia/Bangkok')).replace(tzinfo=None)
        item.add_value("created_at", today)

        yield item.load_item()

