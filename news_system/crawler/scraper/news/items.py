# -*- coding: utf-8 -*-

from scrapy.item import Item, Field

class NewsItems(Item):
    title = Field(default=None)
    source_url = Field(default=None)
    published_date = Field(default=None)
    category = Field(default=None)
    brief_content = Field(default=None)
    content = Field(default=None)
    summary = Field(default=None)
    rank = Field(default=None)
    recommend_date = Field(default=None)
    site = Field(default=None)
    stock_code = Field(default=None)
    created_at = Field(default=None)
    classification_score = Field(default=0)
    rank_score = Field(default=0)
    text_rank = Field(default=None)
    reviewed = Field(default=0)
