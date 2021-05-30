source /home/ubuntu/anaconda3/etc/profile.d/conda.sh
conda activate ainews

## Category 2: Morning brief
# Group 2.2: real_estate
timeout 5m scrapy crawl Qandme -a group=socialtrend -a start_url=https://qandme.net/vi/baibaocao/ -a root_url=https://qandme.net -a next_link="https://qandme.net/home/index/page/{0}/category/keyword/" -a limit=200 & \
timeout 5m scrapy crawl kenh14 -a group=socialtrend -a start_url=https://kenh14.vn/xu-huong.html -a root_url=https://kenh14.vn -a next_link="https://kenh14s.cnnd.vn/tag-news-per.chn?tag_url=xu-huong&page={0}&catids=" & \
timeout 5m scrapy crawl zingnews -a group=socialtrend -a limit=5000 &




