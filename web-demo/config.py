"""App configuration."""
from os import environ
import redis
import json


class Config:
    """Set Flask configuration vars from .env file."""

    # General Config
    SECRET_KEY = 'secret!'

    # Flask-Session
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.from_url('redis://localhost:6379')


group_map_morning = {
    'Banking': "banking",
    'Real estate': "real_estate",
    'Vingroup': "vingroup",
    'Oil and Gas': "oil_and_gas",
    'Food and Drink': "food_and_drink",
    'Others': "others",
    "Social trend": "socialtrend"
}
url_regex = r'(https?):\/\/(.+)'
sites_morning = ['Banking', 'Real estate', 'Vingroup', 'Oil and Gas',
                 'Food and Drink', 'Others', "Social trend"]


group_map_daily = {
    'Macro news': 'macro_news',
    'International news': 'international_news',
    'Stock market news': 'stock_market'
}
sites_daily = ['Macro news', 'International news', 'Stock market news']

vn30 = json.load(open("vn30.json", mode="r", encoding="utf8"))
vn30_helper = {}
for k, v in group_map_morning.items():
    if k == "Social trend":
        continue
    vn30_helper[k] = ["All"]
    for c in vn30:
        if c['group'] == v:
            vn30_helper[k].append(c['code'])

stock_map_morning = {
    "Select a group": ["-"],
    "Banking": vn30_helper["Banking"],
    'Real estate': vn30_helper["Real estate"],
    'Vingroup': vn30_helper["Vingroup"],
    'Oil and Gas': vn30_helper["Oil and Gas"],
    'Food and Drink': vn30_helper["Food and Drink"],
    'Others': vn30_helper["Others"],
    "Social trend": ["-"]
}
