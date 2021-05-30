source /home/ubuntu/anaconda3/etc/profile.d/conda.sh
conda activate ainews

## Category 1: Important News
# Group 1.3:  Vietnamese stock market news

# Cafef 2
timeout 5m scrapy crawl CafeF -a group=stock_market -a start_url=https://cafef.vn/doanh-nghiep.chn -a root_url=https://cafef.vn -a next_link="https://cafef.vn/timeline/36/trang-{0}.chn"   -a limit=100 && \
# Vietnambiz 2
timeout 5m scrapy crawl Vietnambiz -a group=stock_market -a start_url=https://vietnambiz.vn/chung-khoan.htm -a root_url=https://vietnambiz.vn -a next_link="https://vietnambiz.vn/chung-khoan/trang-{0}.htm"   -a limit=100 & \
timeout 5m scrapy crawl Vietnambiz -a group=stock_market -a start_url=https://vietnambiz.vn/doanh-nghiep.htm -a root_url=https://vietnambiz.vn -a next_link="https://vietnambiz.vn/doanh-nghiep/trang-{0}.htm"    -a limit=100 && \ 
timeout 5m scrapy crawl Vietstock -a group=stock_market -a start_url=https://vietstock.vn/doanh-nghiep/hoat-dong-kinh-doanh.htm -a root_url=https://vietstock.vn   -a limit=100 & \
timeout 5m scrapy crawl Vietstock -a group=stock_market -a start_url=https://vietstock.vn/doanh-nghiep/co-tuc.htm -a root_url=https://vietstock.vn   -a limit=100 &
timeout 5m scrapy crawl Vietnambiz -a group=stock_market -a start_url=https://vietnambiz.vn/tai-chinh.htm -a root_url=https://vietnambiz.vn -a next_link="https://vietnambiz.vn/tai-chinh/trang-{0}.htm"   -a limit=100 & \
