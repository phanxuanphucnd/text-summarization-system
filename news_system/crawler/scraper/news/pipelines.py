# -*- coding: utf-8 -*-

from summarizer.ViTextRank import ViTextRank
from ranking import TFRanking

ranking = TFRanking(config_file="./ranking/config_ranking.yaml", code_file="./ranking/stock_code.yaml")

text_rank = ViTextRank()

from classifier import Classifier

import pymongo
import pytz


class ScraperPipeline:
    def process_item(self, item, spider):
        """
        :param item: news items
        :param spider:
        :process
        """
        return item
    

class MongoPipeline(object):
    collection_name = 'news_tbl'

    def __init__(self, mongo_uri, mongo_db, mongo_username, mongo_password, mongo_primary_key, mongo_secondary_key,
                 daily_news_model, morning_brief_model):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_username = mongo_username
        self.mongo_password = mongo_password
        self.mongo_primary_key = mongo_primary_key
        self.mongo_secondary_key = mongo_secondary_key
        self.classifier_daily = Classifier(daily_news_model)
        self.classifier_morning = Classifier(morning_brief_model)

    @classmethod
    def from_crawler(cls, crawler):
        ## pull in information from settings.py
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE'),
            mongo_username=crawler.settings.get('MONGO_USERNAME'),
            mongo_password=crawler.settings.get('MONGO_PASSWORD'),
            mongo_primary_key=crawler.settings.get('MONGO_PRIMARY_KEY'),
            mongo_secondary_key=crawler.settings.get('MONGO_SECONDARY_KEY'),
            daily_news_model=crawler.settings.get('DAILYNEWS_MODEL'),
            morning_brief_model=crawler.settings.get('MORNING_BRIEF_MODEL')
        )

    def open_spider(self, spider):
        ## initializing spider
        ## opening db connection
        self.client = pymongo.MongoClient(self.mongo_uri,
                                          username=self.mongo_username,
                                          password=self.mongo_password,
                                          authSource='admin')
        self.db = self.client[self.mongo_db]
        self.db[self.collection_name].create_index(
            [(self.mongo_primary_key, pymongo.ASCENDING), (self.mongo_secondary_key, pymongo.ASCENDING)], unique=True)

    def close_spider(self, spider):
        ## clean up when spider is closed
        self.client.close()

    def process_item(self, item, spider):

        ## summary
        try:
            doc = item['content']
            item['summary'] = item['brief_content']
            item['text_rank'] = item['brief_content']
            if len(doc) > len(item['text_rank']) * 3 and len(doc.split()) > 50:
                try:
                    if item['category'] != 'macro_news' and \
                            item['category'] != 'international_news' and \
                            item['category'] != 'stock_market':
                        item['text_rank'] = item['text_rank'] + "\n" + text_rank.run(doc, ratio=0.1, max_words=max(0, len(item['brief_content'].split()) - 40))
                    else:
                        item['text_rank'] = item['text_rank'] + "\n" + text_rank.run(doc, ratio=0.1, max_words=-1)
                except Exception as ex:
                    print("===>", ex)
                    pass
            else:
                item['text_rank'] = doc
        except:
            pass

        # classify
        doc_to_classify = item['title'] + "\n" + item['brief_content']
        label = {
            "class": item['category'],
            "score": 1.0
        }
        if 'stock_code' not in item.keys():
            item['stock_code'] = None
        type = 1
        if item['category'] != 'macro_news' and \
                item['category'] != 'international_news' and \
                item['category'] != 'stock_market' and \
                item['category'] != 'social_trend' and \
                item['stock_code'] is None:
            label = self.classifier_morning.predict(sample=doc_to_classify)
            type = 2
        else:
            if item['stock_code'] is None and item['category'] != 'social_trend':
                label = self.classifier_daily.predict(sample=doc_to_classify)
        #
        item['category'] = label['class']
        try:
            item['classification_score'] = label['score'].item()
        except:
            item['classification_score'] = label['score']

        ## how to handle each post
        news_rank = ranking.get_rank(title=item['title'], brief_content=item['brief_content'], content=item['content'],
                                     prior_category=item.get("category", 'macro_news'), code=item['stock_code'])

        try:
            if 'stock_code' not in item.keys():
                item['stock_code'] = "---"
            if item['stock_code'] is None:
                item['stock_code'] = "---"
        except:
            item['stock_code'] = "---"
            pass
        item['reviewed'] = 0
        # if item['stock_code'] is not "---":
        #     item['rank_score'] = 1000
        #     item['rank'] = 1
        # else:
        item['rank'] = news_rank['rank']
        item['rank_score'] = news_rank['score'] * 100
        if type == 2:
            item['stock_code'] = news_rank['code']

        if self.db[self.collection_name].find({"source_url": item["source_url"], "reviewed": {"$gt": 1}}).limit(1).count() < 1:
            self.db[self.collection_name].insert(dict(item))
            spider.force_stop = False
            return item
        url = item['source_url']
        cat = item['category']
        del item['category']
        del item['source_url']
        try:
            del item['created_at']
        except:
            pass
        self.db[self.collection_name].update_one(
            {"source_url": url, "category": cat, "$or": [{"reviewed": {"$exists": False}}, {"reviewed": 0}]}, {"$set": item})
        return item
