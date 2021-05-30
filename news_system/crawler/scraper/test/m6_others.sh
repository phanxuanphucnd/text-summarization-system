source /home/ubuntu/anaconda3/etc/profile.d/conda.sh
conda activate ainews

## Category 2: Morning brief
# Group 2.2: real_estate

timeout 5m scrapy crawl stockbizvn -a group=others  -a start_url="https://www.stockbiz.vn/Stocks/SSI/CompanyNews.aspx" -a stock_code=SSI  -a limit=100 & \
timeout 5m scrapy crawl stockbizvn -a group=others  -a start_url="https://www.stockbiz.vn/Stocks/VJC/CompanyNews.aspx" -a stock_code=VJC  -a limit=100 & \
timeout 5m scrapy crawl stockbizvn -a group=others  -a start_url="https://www.stockbiz.vn/Stocks/FPT/CompanyNews.aspx" -a stock_code=FPT  -a limit=100 && \
timeout 5m scrapy crawl stockbizvn -a group=others  -a start_url="https://www.stockbiz.vn/Stocks/MWG/CompanyNews.aspx" -a stock_code=MWG  -a limit=100 & \
timeout 5m scrapy crawl stockbizvn -a group=others  -a start_url="https://www.stockbiz.vn/Stocks/PNJ/CompanyNews.aspx" -a stock_code=PNJ  -a limit=100 & \
timeout 5m scrapy crawl stockbizvn -a group=others  -a start_url="https://www.stockbiz.vn/Stocks/REE/CompanyNews.aspx" -a stock_code=REE  -a limit=100 && \
timeout 5m scrapy crawl stockbizvn -a group=others  -a start_url="https://www.stockbiz.vn/Stocks/HPG/CompanyNews.aspx" -a stock_code=HPG  -a limit=100 & \

timeout 5m scrapy crawl financevietstock -a group=others -a start_url=https://finance.vietstock.vn/VJC/tin-tuc-su-kien.htm  -a stock_code=VJC  -a limit=100 & \
timeout 5m scrapy crawl financevietstock -a group=others -a start_url=https://finance.vietstock.vn/FPT/tin-tuc-su-kien.htm  -a stock_code=FPT  -a limit=100 && \
timeout 5m scrapy crawl financevietstock -a group=others -a start_url=https://finance.vietstock.vn/MWG/tin-tuc-su-kien.htm  -a stock_code=MWG  -a limit=100 & \
timeout 5m scrapy crawl financevietstock -a group=others -a start_url=https://finance.vietstock.vn/PNJ/tin-tuc-su-kien.htm  -a stock_code=PNJ  -a limit=100 & \
timeout 5m scrapy crawl financevietstock -a group=others -a start_url=https://finance.vietstock.vn/REE/tin-tuc-su-kien.htm  -a stock_code=REE  -a limit=100 && \
timeout 5m scrapy crawl financevietstock -a group=others -a start_url=https://finance.vietstock.vn/HPG/tin-tuc-su-kien.htm  -a stock_code=HPG  -a limit=100 & \
timeout 5m scrapy crawl financevietstock -a group=others -a start_url=https://finance.vietstock.vn/SSI/tin-tuc-su-kien.htm  -a stock_code=SSI  -a limit=100 &
