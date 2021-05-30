export DISPLAY=:0
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
source /home/ubuntu/anaconda3/etc/profile.d/conda.sh
conda activate ainews

## Category 2: Morning brief
# Group 2.2: real_estate


timeout 5m scrapy crawl stockbizvn -a group=oil_and_gas  -a start_url="https://www.stockbiz.vn/Stocks/GAS/CompanyNews.aspx"  -a stock_code=GAS  -a limit=100 & \
timeout 5m scrapy crawl stockbizvn -a group=oil_and_gas  -a start_url="https://www.stockbiz.vn/Stocks/POW/CompanyNews.aspx"  -a stock_code=POW  -a limit=100 & \
timeout 5m scrapy crawl stockbizvn -a group=oil_and_gas  -a start_url="https://www.stockbiz.vn/Stocks/PXL/CompanyNews.aspx"  -a stock_code=PXL  -a limit=100 && \


timeout 5m scrapy crawl financevietstock -a group=oil_and_gas -a start_url=https://finance.vietstock.vn/GAS/tin-tuc-su-kien.htm   -a stock_code=GAS  -a limit=100 & \
timeout 5m scrapy crawl financevietstock -a group=oil_and_gas -a start_url=https://finance.vietstock.vn/POW/tin-tuc-su-kien.htm   -a stock_code=POW  -a limit=100 & \
timeout 5m scrapy crawl financevietstock -a group=oil_and_gas -a start_url=https://finance.vietstock.vn/PXL/tin-tuc-su-kien.htm   -a stock_code=PXL  -a limit=100 &

