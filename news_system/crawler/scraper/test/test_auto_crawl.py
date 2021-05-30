#!/home/ubuntu/anaconda3/envs/ainews/bin/python
import multiprocessing
import time

from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess

from news.spiders.cafef_spider import CafeFSpider
from news.spiders.stockbizvn_spider import Stockbizvn
from news.spiders.finance_vietstock_spider import FinanceVietstock


if __name__ == '__main__':
    settings = get_project_settings()
    process = CrawlerProcess(settings)

    process.crawl(Stockbizvn, group="banking", start_url="https://www.stockbiz.vn/Stocks/VCB/CompanyNews.aspx",
                  stock_code="VCB", limit=100)
    process.crawl(Stockbizvn, group="banking", start_url="https://www.stockbiz.vn/Stocks/TCB/CompanyNews.aspx",
                  stock_code="TCB", limit=100)
    process.crawl(Stockbizvn, group="banking", start_url="https://www.stockbiz.vn/Stocks/BID/CompanyNews.aspx",
                  stock_code="BID", limit=100)

    process.crawl(FinanceVietstock, group="banking", start_url="https://finance.vietstock.vn/BID/tin-tuc-su-kien.htm",
                  stock_code="BID", limit=100)
    process.crawl(FinanceVietstock, group="banking", start_url="https://finance.vietstock.vn/TCB/tin-tuc-su-kien.htm",
                  stock_code="TCB", limit=100)
    process.crawl(FinanceVietstock, group="banking", start_url="https://finance.vietstock.vn/VCB/tin-tuc-su-kien.htm",
                  stock_code="VCB", limit=100)

    process.start()
    process.stop()

