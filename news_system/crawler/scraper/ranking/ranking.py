# -*- coding: utf-8 -*-

import os
import math
import string
import numpy as np

from typing import Union, Dict, List
from .utils import get_config_yaml, normalize, is_low_priority, is_empty

__mapping__ = {
    'macro_news': 'MACRO_NEWS',
    'international_news': 'INTERNATIONAL_NEWS',
    'stock_market': 'VN_STOCK_MARKET',
    'banking': 'BANKING',
    'oil_and_gas': 'OIL_AND_GAS',
    'food_and_drink': 'FOOD_AND_DRINK',
    'real_estate': 'REAL_ESTATE',
    'vingroup': 'VINGROUP',
    'others': 'OTHERS'
}


class TFRanking(object):
    def __init__(self, config_file: Union[str, Dict] = None, code_file: Union[str, Dict] = None):
        """Initialize a TFRanking object

        :param config_file: Path or Dictionary to the config file, that define keywords in sub-category.
        """

        self.config = None
        if isinstance(config_file, Dict):
            self.config = config_file
        else:
            config = get_config_yaml(config_file=config_file)
            self.config = config

        self.config_code = None
        if isinstance(code_file, Dict):
            self.config_code = code_file
        else:
            config_code = get_config_yaml(config_file=code_file)
            self.config_code = config_code

    def get_stock_code(self, title: str, brief_content: str):
        def clean(str):
            trantab = str.maketrans(dict.fromkeys(list(string.punctuation)))
            str = str.translate(trantab)
            return str.strip().lower()

        def search_one_word(s, w):
            words = s.split()
            words = [clean(x) for x in words]
            if w in words:
                return True
            return False
        sample = title + ' ' + brief_content
        sample = normalize(text=sample, lowercase=True, rm_emoji=True, rm_special_characters=True, rm_url=True)
        self.codes = self.config_code.get('COMPANY', None)
        # print("--->", self.codes)
        for _, values in self.codes.items():
            code = values.get('code', None)
            keywords = values.get('keywords', None)
            # print("===>", code, keywords)
            for keyword in keywords:
                if len(keyword.split()) > 1:
                    if sample.count(keyword.lower()) > 0:
                        return code
                else:
                    if search_one_word(sample, keyword.lower()):
                        return code
        return "---"

    def get_group(self, category: str):
        if category.lower() in ['macro_news', 'international_news', 'stock_market']:
            return 'daily_news'
        else:
            return 'morning_brief'

    def get_rank(
            self,
            title: str,
            brief_content: str,
            content: str,
            prior_category: str,
            code: str = "---",
            **kwargs
    ):
        """Function to get the rank of news (the order of priority to displayed on the home page. 
        
        :param title: (str) The title of article 
        :param brief_content: (str) The brief_content of article 
        :param content: (str) The content of article 
        :param prior_category: (str) The category of news is categorized before ranking

        :returns: The result format: \n
                    { \n
                        'rank': 1, \n
                        'score': 0.5322 \n, 
                        'name_rank': 'state_bank' \n
                        'code': None
                    }
        """
        if prior_category not in __mapping__:
            print(f"Warning: `prior_category` not in catebogry must be ranking. ")
            return {
                'rank': 1,
                'score': -1,
                'name_rank': "none",
                'code': code
            }

        self.data = self.config.get(__mapping__[prior_category], None)
        self.num_ranking = len(self.data)
        group = self.get_group(prior_category)

        MAX_RANK = 100

        if is_low_priority(title, brief_content, content, group):
            return {
                'rank': MAX_RANK,
                'score': -1,
                'name_rank': "none",
                'code': code
            }

        if is_empty(title):
            title = ''
        if is_empty(brief_content):
            brief_content = ''
        if is_empty(content):
            content = ''

        if code == "---" or code is None:
            code = self.get_stock_code(title, brief_content)
        else:
            return {
                'rank': 1,
                'score': 10,
                'name_rank': "top priority",
                'code': code
            }
        
        title_2_brief = title + ' ' + brief_content
        title_2_brief = normalize(
            text=title_2_brief, lowercase=True, rm_emoji=True, rm_special_characters=True, rm_url=True)

        title_2_content = title + ' ' + brief_content + ' ' + content
        title_2_content = normalize(
            text=title_2_content, lowercase=True, rm_emoji=True, rm_special_characters=True, rm_url=True)

        def split_text(str):
            trantab = str.maketrans(dict.fromkeys(list(string.punctuation)))
            str = str.translate(trantab)
            str = str.strip().lower()

            return str.split()

        # title_2_brief = split_text(title_2_brief)
        # title_2_content = split_text(title_2_content)

        # bowCount = len(sample.split(' '))


        output = {}
        for rank, values in self.data.items():
            output[rank] = 0
            keywords = values.get('keywords', None)

            for kw in keywords:
                if rank == 1 and group == 'morning_brief':
                    temp = title_2_brief.count(kw.lower())
                    # print(f"\n- kw: {kw}: {temp}")
                else:
                    temp = title_2_content.count(kw.lower())
                    # print(f"\n- kw: {kw}: {temp}")

                # temp = temp / math.sqrt(bowCount)
                output[rank] += temp


        if group == 'daily_news':
            MAX_SCORE = 1
            RANK = MAX_RANK
        else:
            MAX_SCORE = 0
            RANK = MAX_RANK

        ## Get MAX_SCORE and return Rank    
        for k, v in output.items():
            if v > MAX_SCORE:
                RANK = k
                MAX_SCORE = v

        return {
            'rank': int(RANK),
            'score': MAX_SCORE,
            'name_rank': '',
            'code': code
        }


class RuleRanking(object):
    def __init__(self, config_file: Union[str, Dict] = None):
        """Initialize a Rule-based Ranking object

        :param config_file: Path or Dictionary to the config file, that define keywords in sub-category.
        """

        self.config = None
        if isinstance(config_file, Dict):
            self.config = config_file
        else:
            config = get_config_yaml(config_file=config_file)
            self.config = config

    def get_rank(
            self,
            title: str,
            brief_content: str,
            content: str,
            prior_category: str,
            **kwargs
    ):
        """Function to get the rank of news (the order of priority to displayed on the home page. 
        
        :param title: (str) The title of article 
        :param brief_content: (str) The brief_content of article 
        :param content: (str) The content of article 
        :param prior_category: (str) The category of news is categorized before ranking

        :returns: The result format: \n
                    { \n
                        'rank': 1, \n
                        'score': 0.5322 \n, _
                        'name_rank': 'state_bank' \n
                    }
        """
        if prior_category not in __mapping__:
            print(f"Warning: `prior_category` not in catebogry must be ranking. ")
            return {
                'rank': 1,
                'score': 1,
                'name_rank': "none"
            }

        self.data = self.config.get(__mapping__[prior_category], None)
        self.num_ranking = len(self.data)

        if is_low_priority(title, brief_content, content):
            return {
                'rank': self.num_ranking,
                'score': -1,
                'name_rank': "none"
            }

        if is_empty(title):
            title = ''
        if is_empty(brief_content):
            brief_content = ''
        if is_empty(content):
            content = ''

        
        sample = title + ' ' + brief_content + ' ' + content
        sample = normalize(text=sample, lowercase=True, rm_emoji=True, rm_special_characters=True, rm_url=True)

        RANK = self.num_ranking
        SCORE = 1
        for rank, values in self.data.items():
            keywords = values.get('keywords', None)

            for kw in keywords:
                if kw in sample:
                    RANK = rank
                    return {
                        'rank': int(RANK),
                        'score': SCORE,
                        'name_rank': self.data[RANK].get('name', None)
                    }

        return {
            'rank': int(RANK),
            'score': SCORE,
            'name_rank': self.data[RANK].get('name', None)
        }
