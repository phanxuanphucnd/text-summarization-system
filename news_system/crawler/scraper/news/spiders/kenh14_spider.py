# -*- coding: utf-8 -*-

from scrapy import Spider
from scrapy.http import Request
from news.items import NewsItems
from news.loader import NewsLoader

'''
Spider class for crawl pages
'''


class kenh14Spider(Spider):
    # Crawling CafeF example
    name = 'kenh14'

    # scrapy crawl CafeF -a group=macro -a start_url=https://cafef.vn/vi-mo-dau-tu.chn \
    # -a root_url=https://cafef.vn -a next_link="https://cafef.vn/timeline/33/trang-{0}.chn"

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
        # print(self.page, next_page)
        news_links = []
        links = response.xpath(
            "//li[@class='knswli need-get-value-facebook clearfix']/div[@class='knswli-left "
            "fl']/a/@href").getall()
        print(links)
        # return
        for link in links:
            link = self.root_url + link
            if link not in news_links:
                news_links.append(link)


        for news_link in news_links:
            yield Request(
                url=news_link,
                callback=self.extract_news
            )

        # return

        if len(news_links) != 0:
            yield Request(
                url=next_page,
                callback=self.parse_list_page
            )

    def extract_news(self, response):
        """Function to extract content of new from html

        :param response: raw data of a news page
        
        """
        if self.limit > 0 and self.num_news > self.limit:
            return
        self.num_news += 1
        item = NewsLoader(item=NewsItems(), response=response, date_fmt=["%H:%M %d/%m/%Y"],
                          date_regex="((\d{2}):(\d{2}) (\d{2})/(\d{2})/(\d{4}))")
        entry = response.xpath("//div[@class='klw-new-content']")[0]
        title = response.xpath("//h1[@class='kbwc-title']/text()").get().strip()
        created_date = response.xpath("//span[@class='kbwcm-time']/text()").get().strip()
        source_url = response.request.url
        try:
            brief_content = "".join(entry.xpath(".//h2[@class='knc-sapo']/descendant::text()").getall()).strip()
        except:
            brief_content = title
        if len(brief_content) == 0:
            brief_content = title
        main_content = ""
        for p in entry.xpath(".//div[@class='knc-content']/p"):
            main_content = "\n".join([main_content, "".join(p.xpath("./descendant::text()").getall()).strip()])
        for p in entry.xpath(".//div[@class='knc-content']/div"):
            main_content = "\n".join([main_content, "".join(p.xpath("./descendant::text()").getall()).strip()])
        if len(main_content) == 0:
            main_content = brief_content
        category = self.group

        item.add_value("title", title)
        item.add_value("published_date", item.find_published_date(created_date))
        item.add_value("source_url", source_url)
        item.add_value("brief_content", brief_content)
        item.add_value("content", main_content)
        item.add_value("category", category)
        item.add_value("site", "https://kenh14.vn")

        from datetime import datetime
        import pytz
        today = datetime.now(pytz.timezone('Asia/Bangkok')).replace(tzinfo=None)
        item.add_value("created_at", today)

        yield item.load_item()
