# NEWS SCRAPER

## Install chrome vs chromedriver on linux server

```
sudo apt install -y libxss1 libappindicator1 libindicator7 xvfb 
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt install -y -f
wget https://chromedriver.storage.googleapis.com/87.0.4280.20/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
mv chromedriver ~/ai-news/news_system/crawler/scraper/drivers/.
chmod +x ~/ai-news/news_system/crawler/scraper/drivers/chromedriver
```