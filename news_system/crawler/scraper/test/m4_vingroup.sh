source /home/ubuntu/anaconda3/etc/profile.d/conda.sh
conda activate ainews

## Category 2: Morning brief
# Group 2.2: real_estate

timeout 5m scrapy crawl stockbizvn -a group=vingroup  -a start_url="https://www.stockbiz.vn/Stocks/VIC/CompanyNews.aspx"  -a stock_code=VIC  -a limit=100 & \
timeout 5m scrapy crawl stockbizvn -a group=vingroup  -a start_url="https://www.stockbiz.vn/Stocks/VRE/CompanyNews.aspx"  -a stock_code=VRE  -a limit=100 & \
timeout 5m scrapy crawl stockbizvn -a group=vingroup  -a start_url="https://www.stockbiz.vn/Stocks/VHM/CompanyNews.aspx"  -a stock_code=VHM  -a limit=100 && \

timeout 5m scrapy crawl financevietstock -a group=vingroup -a start_url=https://finance.vietstock.vn/VIC/tin-tuc-su-kien.htm   -a stock_code=VIC  -a limit=100 & \
timeout 5m scrapy crawl financevietstock -a group=vingroup -a start_url=https://finance.vietstock.vn/VRE/tin-tuc-su-kien.htm   -a stock_code=VRE  -a limit=100 & \
timeout 5m scrapy crawl financevietstock -a group=vingroup -a start_url=https://finance.vietstock.vn/VHM/tin-tuc-su-kien.htm   -a stock_code=VHM  -a limit=100 & 
