source /home/ubuntu/anaconda3/etc/profile.d/conda.sh
conda activate ainews

## Category 2: Morning brief
# Group 2.2: real_estate

timeout 5m scrapy crawl stockbizvn -a group=real_estate  -a start_url="https://www.stockbiz.vn/Stocks/ROS/CompanyNews.aspx"  -a stock_code=ROS  -a limit=100 & \
timeout 5m scrapy crawl stockbizvn -a group=real_estate  -a start_url="https://www.stockbiz.vn/Stocks/NVL/CompanyNews.aspx"  -a stock_code=NVL  -a limit=100 & \
timeout 5m scrapy crawl stockbizvn -a group=real_estate  -a start_url="https://www.stockbiz.vn/Stocks/TCH/CompanyNews.aspx"  -a stock_code=TCH  -a limit=100 && \
timeout 5m scrapy crawl stockbizvn -a group=real_estate  -a start_url="https://www.stockbiz.vn/Stocks/KDH/CompanyNews.aspx"  -a stock_code=KDH  -a limit=100 & \


timeout 5m scrapy crawl financevietstock -a group=real_estate -a start_url=https://finance.vietstock.vn/ROS/tin-tuc-su-kien.htm   -a stock_code=ROS  -a limit=100 & \
timeout 5m scrapy crawl financevietstock -a group=real_estate -a start_url=https://finance.vietstock.vn/FLC/tin-tuc-su-kien.htm   -a stock_code=FLC  -a limit=100 && \
timeout 5m scrapy crawl financevietstock -a group=real_estate -a start_url=https://finance.vietstock.vn/TCH/tin-tuc-su-kien.htm   -a stock_code=TCH  -a limit=100 & \
timeout 5m scrapy crawl financevietstock -a group=real_estate -a start_url=https://finance.vietstock.vn/KDH/tin-tuc-su-kien.htm   -a stock_code=KDH  -a limit=100 & 

