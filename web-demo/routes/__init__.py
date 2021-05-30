from flask import Blueprint

routes = Blueprint('routes', __name__)

from routes.daily_news import *
from routes.accounts import *
from routes.morning_brief import *
from routes.vn_30 import *