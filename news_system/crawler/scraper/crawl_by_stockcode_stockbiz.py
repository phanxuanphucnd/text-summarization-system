#!/home/ubuntu/anaconda3/envs/ainews/bin/python
import argparse
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess

from news.spiders.stockbizvn_spider import Stockbizvn
from news.spiders.finance_vietstock_spider import FinanceVietstock


import json


def parse_args():
    """Function to parse config file to get list of stock code
    :returns: parser object
    """
    parser = argparse.ArgumentParser(description="Automated script for crawl banking news")
    parser.add_argument('--from_file', type=str, default='./vn30/banking_1.json')
    return parser


if __name__ == '__main__':
    """
    Crawl news from finance.vietstock.vn and stockbiz.vn for input stock code
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

    stock_list = json.load(open(args.from_file, "r"))

    for stock in stock_list:
        process.crawl(Stockbizvn, group=stock['group'],
                      start_url="https://www.stockbiz.vn/Stocks/{0}/CompanyNews.aspx".format(stock['code']),
                      stock_code=stock['code'], limit=50)


    process.start()
    process.stop()
