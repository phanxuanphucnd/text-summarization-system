source /home/ubuntu/anaconda3/etc/profile.d/conda.sh
conda activate ainews

## Category 2: Morning brief
# Group 2.2: real_estate

timeout 5m scrapy crawl stockbizvn -a group=food_and_drink  -a start_url="https://www.stockbiz.vn/Stocks/SAB/CompanyNews.aspx" -a stock_code=SAB  -a limit=100 & \
timeout 5m scrapy crawl stockbizvn -a group=food_and_drink  -a start_url="https://www.stockbiz.vn/Stocks/VNM/CompanyNews.aspx" -a stock_code=VNM  -a limit=100 & \
timeout 5m scrapy crawl stockbizvn -a group=food_and_drink  -a start_url="https://www.stockbiz.vn/Stocks/MSN/CompanyNews.aspx" -a stock_code=MSN  -a limit=100 && \
timeout 5m scrapy crawl stockbizvn -a group=food_and_drink  -a start_url="https://www.stockbiz.vn/Stocks/SBT/CompanyNews.aspx" -a stock_code=SBT  -a limit=100 & \

timeout 5m scrapy crawl financevietstock -a group=food_and_drink -a start_url="https://finance.vietstock.vn/MSN/tin-tuc-su-kien.htm"  -a stock_code=MSN  -a limit=100 & \
timeout 5m scrapy crawl financevietstock -a group=food_and_drink -a start_url="https://finance.vietstock.vn/SBT/tin-tuc-su-kien.htm"  -a stock_code=SBT  -a limit=100 && \
timeout 5m scrapy crawl financevietstock -a group=food_and_drink -a start_url="https://finance.vietstock.vn/SAB/tin-tuc-su-kien.htm"  -a stock_code=SAB  -a limit=100 & \
timeout 5m scrapy crawl financevietstock -a group=food_and_drink -a start_url="https://finance.vietstock.vn/VNM/tin-tuc-su-kien.htm"  -a stock_code=VNM  -a limit=100 &


