# -*- coding: utf-8 -*-

import os
import re
import regex
import yaml 

from typing import Any, Text, Union
from unicodedata import normalize as nl

def is_empty(text: Text) -> bool:
    return text is None or text == ''

def normalize(
    text: Text=None, 
    form: Text='NFKC', 
    lowercase: bool=True, 
    rm_url: bool=False, 
    rm_emoji: bool=False, 
    rm_special_characters: bool=False
) -> Any:
    """Function to normalize text input
    
    :param text: (str) Text input
    :param form: (str) Unicode nornalize forms (default: 'NFKC')
    :param lowercase: (bool) If True, lowercase text (default: True)
    :param rm_url: (bool) If True, remove url token (default: True)
    :param rm_emoji: (bool) If True, remove emoji token (default: True)
    :param rm_special_characters: (bool) If True, remove special characters (default: True)

    :returns: Text after normalized.
    """
    if is_empty(text):
        return None

    text = nl(form, text).strip()
    
    # lowercase 
    if lowercase:
        text = text.lower().strip()
    
    # Remove emoji
    if rm_emoji:
        emoji_pattern = regex.compile("["
                                    u"\U0001F600-\U0001F64F"  # emoticons
                                    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                    u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                    u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                    "]+", flags=regex.UNICODE)
        text = emoji_pattern.sub(r" ", text) 
    
    # Remove url, link
    if rm_url:
        url_regex = re.compile(r'\bhttps?://\S+\b')
        text = url_regex.sub(r" ", text)

    # Remove special token and duplicate <space> token
    if rm_special_characters:
        text = regex.sub(r"[^%$&a-z0-9A-Z*\sÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠẾếàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸýửữựỳỵỷỹ]", " ", text)
        text = regex.sub(r"\s{2,}", " ", text)

    return text


def get_config_yaml(config_file: str):
    """This function will parse the configuration file that was provided as a 
    system argument into a dictionary.

    :param config_file: Path to the config file

    :return: A dictionary contraining the parsed config file
    """
    if not isinstance(config_file, str):
        raise TypeError(f"The config must be a file path not {type(config_file)}")
    elif not os.path.isfile(config_file):
        raise FileNotFoundError(f"  File {config_file} is not found!")
    elif not config_file[-5:] == ".yaml":
        raise TypeError(f"We only support .yaml format")
    else:
        print(f"Load config-file from: {config_file}")
        
        with open(config_file, 'r', encoding='utf8') as file:
            cfg_parser = yaml.load(file, Loader=yaml.Loader)

    return cfg_parser

def is_low_priority(title=None, brief_content=None, content=None, group=None):

    if group == "daily_news":
        print(f"\n- Check priority in daily news")
        temp = daily_news_low_priority(title=title, brief_content=brief_content, content=content)
        return temp
    else:
        print(f"\n- Check priority in morning brief")
        temp = morning_brief_low_priority(title=title, brief_content=brief_content, content=content)
        return temp

def daily_news_low_priority(title=None, brief_content=None, content=None):

    if is_empty(title):
        title = ''
    if is_empty(brief_content):
        brief_content = ''
    if is_empty(content):
        content = ''

    ## check điều kiện với title bỏ dấu ? 
    cond_1 = [
        '?'
    ]
    if any(x.lower() in title.lower() for x in cond_1):
        return True

    print(1)
    ## check điều kiện IN với title + brief_content
    ignore_values_2 = [
        # nhận định cá nhân tổ chức
        'ssi research', 'vcsc', 'bảo việt', 

        # các tin tỷ giá ngân hàng (USD/VNĐ, …); tỷ giá ngoại tệ, đô la, euro, USD.
        'tỷ giá usd', 'tỷ giá ngân hàng', 'tỷ giá vnđ', 'tỷ giá ngoại tệ', 'tỷ giá đô la', 'tỷ giá euro', 'bitcoin', 
        "giá usd", 'giá vnđ', 'giá ngoại tệ', 'giá đô la', 'giá dollar', 

        # các tin về giá kim loại
        'giá vàng', 'giá dầu', 'giá sắt', 'giá thép', 'giá đồng', 'giá kim loại', 'giá gas', 'giá xăng', 
        
        # ngày đkcc, chứng quyền, thư mời
        'ngày đăng ký cuối cùng', 'ngày đkcc', 'chứng quyền', 'thư mời', 

        # tin liên quan đến trụ sở, chi nhánh, phòng giao dịch 
        'trụ sở', 'chi nhánh', 'phòng giao dịch', 

        # các tin về lãi suất
        'lãi suất thẻ tín dụng', 'lãi và gốc trái phiếu', 'lãi suất trái phiếu', 'lãi trái phiếu'

        # tin quảng cáo
        'khuyenmai', 'khuyến mại', 'quảng cáo', 'chương trình', 'tri ân', 'may mắn', 'trúng thưởng', 'ưu đãi',
    ]

    brief_text = title + ' ' + brief_content
    brief_text = brief_text.lower()

    if any(x.lower() in brief_text for x in ignore_values_2):
        return True

    print(2)

    ## check điều kiện IN và IN với title + brief_content
    in_cond_1 = [
        'lãi suất', 
    ]
    in_cond_2 = [
        'trái phiếu',
    ]
    if any(x.lower() in brief_text for x in in_cond_1) and any(y.lower() in brief_text for y in in_cond_2):
        return True

    print(3)

    ## check điều kiện IN và not IN với all text 
    all_text = title + ' ' + brief_content + ' ' + content
    all_text = all_text.lower()
    
    ignore_values = [
        # cac  từ khóa 
        'video', 'grafic', 'graphic', 'kỳ 1', 'kỳ 2', 'kỳ 3', 'kỳ 4', 'kỳ 5' 'chart', 
        
        # các tin nhận định của cá nhân tổ chức ko phải bộ trưởng, thủ tướng, ...
        'phát biểu', 'phỏng vấn', 'nhận định', 'quan điểm', 'theo ts.', 'theo giáo sư', 
        'thưa ông', 'theo gs.', 'theo tiến sĩ', 'chuyên gia cho rằng', 'theo chuyên gia', 
        'quan điểm cá nhân', 'theo phân tích của', 'theo đánh giá của', 'theo cá nhân', 'theo tổ chức',


        # tin quảng cáo
        'khuyenmai', 'khuyến mại', 'quảng cáo', 'chương trình', 'tri ân', 'may mắn', 'trúng thưởng', 'ưu đãi',
        
    ]
    cop_values = ['thủ tướng', 'lãnh đạo cấp cao', 'bộ trưởng', 'fed']

    if any(x.lower() in all_text for x in ignore_values) and not any(y.lower() in all_text for y in cop_values):
        return True
    
    print(4)
    
    return False


def morning_brief_low_priority(title=None, brief_content=None, content=None):

    if is_empty(title):
        title = ''
    if is_empty(brief_content):
        brief_content = ''
    if is_empty(content):
        content = ''

    ## check điều kiện với title bỏ dấu ? 
    cond_1 = [
        '?'
    ]
    if any(x.lower() in title.lower() for x in cond_1):
        return True


    ## check điều kiện IN với title + brief_content
    ignore_values_2 = [
        # nhận định cá nhân tổ chức
        'ssi research', 'vcsc', 'bảo việt', 

        # các tin tỷ giá ngân hàng (USD/VNĐ, …); tỷ giá ngoại tệ, đô la, euro, USD.
        'tỷ giá usd', 'tỷ giá ngân hàng', 'tỷ giá vnđ', 'tỷ giá ngoại tệ', 'tỷ giá đô la', 'tỷ giá euro', 'bitcoin', 
        "giá usd", 'giá vnđ', 'giá ngoại tệ', 'giá đô la', 'giá dollar', 

        # các tin về giá kim loại
        # 'giá vàng', 'giá dầu', giá sắt', 'giá thép', 'giá đồng', 'giá kim loại', 'giá gas',  'giá xăng', 
        
        # ngày đkcc, chứng quyền, thư mời
        'ngày đăng ký cuối cùng', 'ngày đkcc', 'chứng quyền', 'thư mời', 

        # tin liên quan đến trụ sở, chi nhánh, phòng giao dịch 
        'trụ sở', 'chi nhánh', 'phòng giao dịch', 

        # các tin về lãi suất
        'lãi suất thẻ tín dụng', 'lãi và gốc trái phiếu', 'lãi suất trái phiếu', 'lãi trái phiếu'

        # tin quảng cáo
        'khuyenmai', 'khuyến mại', 'quảng cáo', 'chương trình', 'tri ân', 'may mắn', 'trúng thưởng', 'ưu đãi',
    ]

    brief_text = title + ' ' + brief_content
    brief_text = brief_text.lower()

    if any(x.lower() in brief_text for x in ignore_values_2):
        return True

    ## những case check điều kiện IN và IN với title + brief_content
    in_cond_1 = [
        'lãi suất', 
    ]
    in_cond_2 = [
        'trái phiếu', 
    ]
    if any(x.lower() in brief_text for x in in_cond_1) and any(y.lower() in brief_text for y in in_cond_2):
        return True


    ## check điều kiện IN và not IN với all text 
    all_text = title + ' ' + brief_content + ' ' + content
    all_text = all_text.lower()
    
    ignore_values = [
        # cac  từ khóa 
        'video', 'grafic', 'graphic', 'kỳ 1', 'kỳ 2', 'kỳ 3', 'kỳ 4', 'kỳ 5' 'chart', 
        
        # các tin nhận định của cá nhân tổ chức ko phải bộ trưởng, thủ tướng, ...
        'phát biểu', 'phỏng vấn', 'nhận định', 'quan điểm', 'theo ts.', 'theo giáo sư', 
        'thưa ông', 'theo gs.', 'theo tiến sĩ', 'chuyên gia cho rằng', 'theo chuyên gia', 
        'quan điểm cá nhân', 'theo phân tích của', 'theo đánh giá của', 'theo cá nhân', 'theo tổ chức',


        # tin quảng cáo
        'khuyenmai', 'khuyến mại', 'quảng cáo', 'chương trình', 'tri ân', 'may mắn', 'trúng thưởng', 'ưu đãi',
        
    ]
    cop_values = ['thủ tướng', 'lãnh đạo cấp cao', 'bộ trưởng', 'fed']

    if any(x.lower() in all_text for x in ignore_values) and not any(y.lower() in all_text for y in cop_values):
        return True
    
    return False

