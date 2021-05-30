# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy.http import Request
from news.items import NewsItems
from news.loader import NewsLoader
from datetime import datetime


class QandmeSpider(Spider):
    name = 'Qandme'

    # scrapy crawl Qandme -a group=socialtrend -a start_url=https://qandme.net/vi/baibaocao/ -a root_url=https://qandme.net -a next_link="https://qandme.net/home/index/page/{0}/category//keyword/" -a limit=500 -o data_qandme.csv

    page = 0
    num_news = 0
    limit = -1

    def __init__(self, category='', **kwargs):
        # super(QandmeSpider, self).__init__(**kwargs)
        # With python 3:
        super().__init__(**kwargs)
        if self.limit != -1:
            self.limit = int(self.limit)


    def start_requests(self):
        yield Request(
            url=self.start_url,
            callback=self.parse_list_page
        )

    def convert_date(self, st):
        return datetime.strptime(st, "%B %d, %Y").strftime('%d-%m-%Y')

    def parse_list_page(self, response):
        """ This spider would start with page, collecting category links, and item links, 
        parsing the latter with this function method

        :param response: response of the start page

        """

        if self.limit > 0 and self.num_news > self.limit:
            return

        next_page = self.next_link.format(self.page)
        self.page += 1

        news_link = []
        news_published_date = []
        list_published_date = response.xpath("//div[@class = 'list-content']//p[1]/text()").extract()
        list_link = response.xpath("//a[@class = 'view-btn']/@href").extract()
        i = 0

        for link in list_link:
            link = self.root_url + link
            if link not in news_link:
                news_link.append(link)
                news_published_date.append(list_published_date[i])

            i += 1

        if len(news_link) != 0:
            yield Request(
                url=next_page,
                callback=self.parse_list_page
            )

        i = 0
        for link in news_link:
            yield Request(url = link, callback=self.extract_news, cb_kwargs=dict(published_date=news_published_date[i]))
            i += 1

    def extract_news(self, response, published_date):
        """Function to extract content of new from html

        :param response: raw data of a news page
        
        """
        if self.limit > 0 and self.num_news > self.limit:
            return
        self.num_news += 1

        item = NewsLoader(item=NewsItems(), response=response, date_fmt=["%B %d, %Y"],
                          date_regex="((January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4})")

        try:
            title = response.xpath("//h1[@class = 'white-color']/text()").getall()[0]
            created_date = published_date
            brief_content = response.xpath("//h2[@class = 'report_note']/text()").getall()[0]
            main_content = " ".join(response.xpath("//p[@class='margin_report']/text()").getall())
            source_url = response.request.url
            category = self.group
        except:
            return

        item.add_value("title", title)
        item.add_value("published_date", created_date)
        item.add_value("source_url", source_url)
        item.add_value("brief_content", brief_content)
        item.add_value("content", main_content)
        item.add_value("category", category)
        item.add_value("site", "https://qandme.net")
        item.add_value("stock_code", "---")

        import pytz
        today = datetime.now(pytz.timezone('Asia/Bangkok')).replace(tzinfo=None)
        item.add_value("created_at", today)

        yield item.load_item()

