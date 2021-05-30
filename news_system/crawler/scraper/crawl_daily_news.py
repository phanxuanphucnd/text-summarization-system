#!/home/ubuntu/anaconda3/envs/ainews/bin/python
# -*- coding: utf-8 -*-

import argparse
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess

from news.spiders.cafef_spider import CafeFSpider
from news.spiders.vietnambiz_spider import VietnambizSpider
from news.spiders.tinnhanhchungkhoan_spider import TinnhanhchungkhoanSpider
from news.spiders.vietstock_spider import VietstockSpider
from news.spiders.sbv_spider import SbvSpider
from news.spiders.vingroup_spider import VingroupSpider
from news.spiders.qandme import QandmeSpider
from news.spiders.kenh14_spider import kenh14Spider
from news.spiders.zingnews_spider import ZingnewsSpider
from news.spiders.ndh_spider import ndhSpider

spiders = [CafeFSpider, VietnambizSpider, TinnhanhchungkhoanSpider, VietstockSpider, SbvSpider, VingroupSpider,
           QandmeSpider, kenh14Spider, ZingnewsSpider]
import json


def parse_args():
    """Function to parse config file to get list of parser
    :returns: parser object
    """
    parser = argparse.ArgumentParser(description="Automated script for crawl banking news")
    parser.add_argument('--from_file', type=str, default='./daily_news/macro_news_1.json')
    return parser


if __name__ == '__main__':
    """
    Crawl news following configuration
    """
    parser = parse_args()
    args = parser.parse_args()
    settings = get_project_settings()
    process = CrawlerProcess(settings)

    #
    # process.crawl(CafeFSpider, group="macro_news", start_url="https://cafef.vn/vi-mo-dau-tu.chn",
    #               root_url="https://cafef.vn", next_link="https://cafef.vn/timeline/33/trang-{0}.chn", limit=100)
    #
    # process.crawl(CafeFSpider, group="macro_news", start_url="https://cafef.vn/tai-chinh-ngan-hang.chn",
    #               root_url="https://cafef.vn", next_link="https://cafef.vn/timeline/34/trang-{0}.chn", limit=100)

    options = json.load(open(args.from_file, "r"))

    for option in options:
        spider = next(item for item in spiders if item.name == option["name"])
        del option["name"]
        print(spider)
        print(option)
        process.crawl(spider, **option)

    process.start()
    process.stop()
