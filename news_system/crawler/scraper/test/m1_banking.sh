source /home/ubuntu/anaconda3/etc/profile.d/conda.sh
conda activate ainews

## Category 2: Morning brief
# Group 2.1:  Banking

timeout 5m scrapy crawl stockbizvn -a group=banking  -a start_url="https://www.stockbiz.vn/Stocks/BID/CompanyNews.aspx" -a stock_code=BID   -a limit=100 & \
timeout 5m scrapy crawl stockbizvn -a group=banking  -a start_url="https://www.stockbiz.vn/Stocks/CTG/CompanyNews.aspx" -a stock_code=CTG   -a limit=100 && \
timeout 5m scrapy crawl stockbizvn -a group=banking  -a start_url="https://www.stockbiz.vn/Stocks/TCB/CompanyNews.aspx" -a stock_code=TCB   -a limit=100 & \
timeout 5m scrapy crawl stockbizvn -a group=banking  -a start_url="https://www.stockbiz.vn/Stocks/VPB/CompanyNews.aspx" -a stock_code=VPB   -a limit=100 & \
timeout 5m scrapy crawl stockbizvn -a group=banking  -a start_url="https://www.stockbiz.vn/Stocks/MBB/CompanyNews.aspx" -a stock_code=MBB   -a limit=100 && \
timeout 5m scrapy crawl stockbizvn -a group=banking  -a start_url="https://www.stockbiz.vn/Stocks/HDB/CompanyNews.aspx" -a stock_code=HDB   -a limit=100 & \
timeout 5m scrapy crawl stockbizvn -a group=banking  -a start_url="https://www.stockbiz.vn/Stocks/EIB/CompanyNews.aspx" -a stock_code=EIB   -a limit=100 & \
timeout 5m scrapy crawl stockbizvn -a group=banking  -a start_url="https://www.stockbiz.vn/Stocks/STB/CompanyNews.aspx" -a stock_code=STB   -a limit=100 && \


timeout 5m scrapy crawl financevietstock -a group=banking -a start_url="https://finance.vietstock.vn/TCB/tin-tuc-su-kien.htm"  -a stock_code=TCB  -a limit=100 & \
timeout 5m scrapy crawl financevietstock -a group=banking -a start_url="https://finance.vietstock.vn/VCB/tin-tuc-su-kien.htm"  -a stock_code=VCB  -a limit=100 & \
timeout 5m scrapy crawl financevietstock -a group=banking -a start_url="https://finance.vietstock.vn/BID/tin-tuc-su-kien.htm"  -a stock_code=BID   -a limit=100 && \
timeout 5m scrapy crawl financevietstock -a group=banking -a start_url="https://finance.vietstock.vn/CTG/tin-tuc-su-kien.htm"  -a stock_code=CTG   -a limit=100 & \
timeout 5m scrapy crawl financevietstock -a group=banking -a start_url="https://finance.vietstock.vn/VPB/tin-tuc-su-kien.htm"  -a stock_code=VPB   -a limit=100 & \
timeout 5m scrapy crawl financevietstock -a group=banking -a start_url="https://finance.vietstock.vn/MBB/tin-tuc-su-kien.htm"  -a stock_code=MBB   -a limit=100 && \
timeout 5m scrapy crawl financevietstock -a group=banking -a start_url="https://finance.vietstock.vn/EIB/tin-tuc-su-kien.htm"  -a stock_code=EIB   -a limit=100 & \
timeout 5m scrapy crawl financevietstock -a group=banking -a start_url="https://finance.vietstock.vn/STB/tin-tuc-su-kien.htm"  -a stock_code=STB   -a limit=100 & \
