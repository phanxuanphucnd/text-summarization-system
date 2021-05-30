# -*- coding: utf-8 -*-
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity, MapCompose, TakeFirst

import datetime
import re
import string


def preprocess_content(x):
    return x


class NewsLoader(ItemLoader):
    def clean(s):
        return s.replace("\r", " ").replace("\t", " ").replace(u"\xa0", " ").replace(u"\u00A0", " ").strip()

    def find_published_date(self, text):
        reg = self.context.get("date_regex")
        match = re.search(reg, "".join(text).strip())
        res = list(filter(lambda x: x, match.groups()) if match else None)
        if res:
            return res[0]
        return None

    def parse_date(date, loader_context):
        for fmt in loader_context.get("date_fmt", []):
            try:
                return datetime.datetime.strptime(date, fmt)
            except ValueError:
                pass
        return None

    def mask(s):
        regex = [
            # {
            #     "regex": r'(http[s]|ftp)?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            #     "mask": "<link_spam>"
            # }
        ]
        for r in regex:
            s = re.sub(r['regex'], r['mask'], s)
        return s

    def parse_content(s):
        s = re.sub(' +', ' ', s)
        lines = re.split(r"\.|\n", s)
        lines = [x.strip() for x in lines]
        lines = [x for x in lines if len(x) > 0]
        return ". ".join(lines)

    default_output_processor = TakeFirst()
    published_date_in = MapCompose(clean, parse_date)
    content_in = MapCompose(clean, mask, parse_content)
    brief_content_in = MapCompose(clean)
    title_in = MapCompose(clean)
