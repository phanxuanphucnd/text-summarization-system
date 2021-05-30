import re
import regex
import pandas as pd

from pandas import DataFrame
from typing import Any, Text
from unicodedata import normalize as nl
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report

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

def normalize_df(
    data_df: DataFrame=None, 
    col: Text='text', 
    form: Text='NFKC', 
    lowercase: bool=True, 
    rm_url: bool=False, 
    rm_emoji: bool=False, 
    rm_special_characters: bool=False
) -> DataFrame:
    
    data_df[col] = data_df[col].apply(lambda x: normalize(
        x, form=form, lowercase=lowercase, rm_emoji=rm_emoji, rm_url=rm_url, rm_special_characters=rm_special_characters))
    
    return data_df

def get_metric(y_true, y_pred):
    
    """Function to get metrics evaluation
    
    :param y_pred: Ground truth (correct) target values
    :param y_true: Estimated targets as returned by a classifier
    
    :returns: acc, f1, precision, recall metrics.
    """

    acc       = accuracy_score(y_true, y_pred)
    f1        = f1_score(y_true, y_pred, average="weighted")
    precision = precision_score(y_true, y_pred, average="weighted")
    recall    = recall_score(y_true, y_pred,  average="weighted")
    report = classification_report(y_true=y_true, y_pred=y_pred)

    return acc, f1, precision, recall, report



def fill_text(data_df):
    """Function fill field `text` in DataFrame if not exists
    :param data_df: A DataFrame

    :returns: Return a DataFrame after filled field `text`

    """
    data_df['text'] = ['']*len(data_df)
    
    for i in range(len(data_df)):
        a = data_df['title'][i]
        b = data_df['brief_content'][i]
        if str(data_df['title'][i]).lower() == 'nan':
            a = ''
        if str(data_df['brief_content'][i]).lower() == 'nan':
            b = ''
        data_df['text'][i] = a + ' ' + b
        
    return data_df