from helpers import *
from config import *
from . import routes

import pandas as pd
from datetime import timedelta, datetime
import re
import pytz
from flask import render_template, session, redirect, request
from flask_paginate import Pagination, get_page_args
import json
from unicodedata import normalize as nl


@routes.route("/daily_news", methods=["GET"])
def daily_news_get():
    if 'user_name' not in session:
        return redirect('/login')

    username_login = session['user_name']

    today = datetime.now(pytz.timezone('Asia/Bangkok')).strftime("%Y-%m-%d")
    yesterday = datetime.now(pytz.timezone('Asia/Bangkok')) - timedelta(1)
    s_date = datetime.strptime(yesterday.strftime(
        "%Y-%m-%d") + " 00:00", "%Y-%m-%d %H:%M")
    e_date = datetime.strptime(today + " 23:59", "%Y-%m-%d %H:%M")

    if request.args.get('page') is None:
        if 'page_data' in session:
            session.pop('page_data', None)
            session.pop('group_name', None)
    limit = 0
    ascending = -1

    if 'page_data' in session:
        data_df = pd.read_json(json.loads(session['page_data']))
        group_name = session['group_name']
        s_date = session['s_date']
        e_date = session['e_date']
        data_shape = data_df.shape
        column_names = data_df.columns.values
        s_date = s_date.strftime("%Y-%m-%d")
        e_date = e_date.strftime("%Y-%m-%d")

        def get_news(offset=0, per_page=10):
            return data_df.iloc[offset: offset + per_page]

        total = len(data_df)
        page, per_page, offset = get_page_args(
            page_parameter='page', per_page_parameter='per_page')
        data_pagination = get_news(offset=offset, per_page=per_page)
        pagination = Pagination(
            page=page, per_page=per_page, total=total, css_framework='bootstrap4')

        return render_template('daily_news.html', tables=data_pagination, data_shape=data_shape,
                               column_names=column_names, page=page, per_page=per_page, pagination=pagination,
                               group=group_name, s_date=s_date, e_date=e_date, sites_daily=sites_daily,
                               username_login=username_login)

    data_df = get_daily_news(None, s_date, e_date, limit, ascending)

    for news in data_df:
        try:
            news['text_rank'] = news['text_rank']
        except:
            news['text_rank'] = news['brief_content']

        news['summary'] = news['brief_content']

        b_content = news['summary']
        b_text_rank = news['text_rank']
        news['word_count'] = len(b_text_rank.split())

        try:
            b_content = b_content.split("\n")
            b_text_rank = b_text_rank.split("\n")
        except:
            b_content = "\n".join(b_content)
            b_content = b_content.split("\n")
            b_text_rank = "\n".join(b_text_rank)
            b_text_rank = b_text_rank.split("\n")

        b_content = [x.strip() for x in b_content]
        b_text_rank = [x.strip() for x in b_text_rank]

        n = 1
        for i, x in enumerate(b_content):
            check = re.match(url_regex, x)
            if check is not None:
                if "vietstock" in x:
                    fname = x[x.rfind("/") + 1:]
                else:
                    fname = "Tài liệu đính kèm {0}".format(n)
                n += 1
                b_content[i] = '<p><a class="text-blue-500" href="{0}" target="_blank">{1}</a></p>'.format(
                    x, fname)
        n = 1
        for i, x in enumerate(b_text_rank):
            check = re.match(url_regex, x)
            if check is not None:
                if "vietstock" in x:
                    fname = x[x.rfind("/") + 1:]
                else:
                    fname = "Tài liệu đính kèm {0}".format(n)
                n += 1
                b_text_rank[i] = '<p><a class="text-blue-500" href="{0}" target="_blank">{1}</a></p>'.format(
                    x, fname)

        del news['brief_content']
        news['summary'] = "<div class='content'>" + \
                          " ".join(b_content) + "</div>"
        news['text_rank'] = "<div class='content'>" + \
                            " ".join(b_text_rank) + "</div>"

    try:
        data_df = pd.DataFrame(data_df)
        data_df["rank"] = data_df["rank"].round(2)
        data_df.sort_values(by=["category", "rank", "reviewed", "published_date", "rank_score"],
                            inplace=True, ascending=[True, True, False, False, False])
        del data_df['rank_score']
        del data_df['reviewed']
    except:
        pass

    if len(data_df) > 0:
        data_df['published_date'] = data_df['published_date'].dt.strftime(
            '%d/%m/%Y %H:%M')
        # del data_df['rank']
        data_columns_index = []
        for value in data_df.columns.values:
            if (value == 'title'):
                data_columns_index.append('Title')
            elif (value == 'category'):
                data_columns_index.append('Category')
            elif (value == 'source_url'):
                data_columns_index.append('Source Url')
            elif (value == 'published_date'):
                data_columns_index.append('Published')
            elif (value == 'summary'):
                data_columns_index.append('Summary')
            elif (value == 'text_rank'):
                data_columns_index.append('Text Rank')
            elif (value == 'word_count'):
                data_columns_index.append('Word Count')
            elif (value == 'rank'):
                data_columns_index.append('Rank')
        data_df.columns = data_columns_index

    session['page'] = 'Daily_News'
    session['page_data'] = json.dumps(data_df.to_json())
    session['group_name'] = None
    session['s_date'] = s_date
    session['e_date'] = e_date
    session['code'] = "---"

    data_shape = data_df.shape
    column_names = data_df.columns.values
    s_date = s_date.strftime("%Y-%m-%d")
    e_date = e_date.strftime("%Y-%m-%d")

    def get_news(offset=0, per_page=10):
        return data_df.iloc[offset: offset + per_page]

    total = len(data_df)
    page, per_page, offset = get_page_args(
        page_parameter='page', per_page_parameter='per_page')
    data_pagination = get_news(offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page,
                            total=total, css_framework='bootstrap4')

    return render_template('daily_news.html', tables=data_pagination, data_shape=data_shape,
                           column_names=column_names, page=page, per_page=per_page, pagination=pagination,
                           group=None, s_date=s_date, e_date=e_date, sites_daily=sites_daily,
                           username_login=username_login)


@routes.route("/daily_news", methods=["POST"])
def daily_news_post():
    if 'user_name' not in session:
        return redirect('/login')

    username_login = session['user_name']

    try:
        group = request.form["search_group"]
        group_name = group
        group = group_map_daily[group]
    except:
        group = None
        group_name = None
    s_date = request.form['search_start_dates']
    e_date = request.form['search_end_dates']
    s_date = datetime.strptime(s_date + " 00:00", "%Y-%m-%d %H:%M")
    e_date = datetime.strptime(e_date + " 23:59", "%Y-%m-%d %H:%M")

    if group is None:
        limit = 0
        ascending = -1

        if 'page_data' in session:
            session.pop('group_name', None)
            session.pop('page_data', None)

        data_df = get_daily_news(group, s_date, e_date, limit, ascending)
        for news in data_df:
            try:
                news['text_rank'] = news['text_rank']
            except:
                news['text_rank'] = news['brief_content']

            news['summary'] = news['brief_content']

            b_content = news['summary']
            b_text_rank = news['text_rank']
            news['word_count'] = len(b_text_rank.split())

            try:
                b_content = b_content.split("\n")
                b_text_rank = b_text_rank.split("\n")
            except:
                b_content = "\n".join(b_content)
                b_content = b_content.split("\n")
                b_text_rank = "\n".join(b_text_rank)
                b_text_rank = b_text_rank.split("\n")

            b_content = [x.strip() for x in b_content]
            b_text_rank = [x.strip() for x in b_text_rank]

            n = 1
            for i, x in enumerate(b_content):
                check = re.match(url_regex, x)
                if check is not None:
                    if "vietstock" in x:
                        fname = x[x.rfind("/") + 1:]
                    else:
                        fname = "Tài liệu đính kèm {0}".format(n)
                    n += 1
                    b_content[i] = '<p><a class="text-blue-500" href="{0}" target="_blank">{1}</a></p>'.format(
                        x, fname)
            n = 1
            for i, x in enumerate(b_text_rank):
                check = re.match(url_regex, x)
                if check is not None:
                    if "vietstock" in x:
                        fname = x[x.rfind("/") + 1:]
                    else:
                        fname = "Tài liệu đính kèm {0}".format(n)
                    n += 1
                    b_text_rank[i] = '<p><a class="text-blue-500" href="{0}" target="_blank">{1}</a></p>'.format(
                        x, fname)

            del news['brief_content']
            news['summary'] = "<div class='content'>" + \
                              " ".join(b_content) + "</div>"
            news['text_rank'] = "<div class='content'>" + \
                                " ".join(b_text_rank) + "</div>"

        try:
            data_df = pd.DataFrame(data_df)
            data_df["rank"] = data_df["rank"].round(2)
            data_df.sort_values(by=["category", "rank", "reviewed", "published_date", "rank_score"],
                                inplace=True, ascending=[True, True, False, False, False])
            del data_df['rank_score']
            del data_df['reviewed']
        except:
            pass

        if (len(data_df) > 0):
            data_df['published_date'] = data_df['published_date'].dt.strftime(
                '%d/%m/%Y %H:%M')
            # del data_df['rank']
            data_columns_index = []
            for value in data_df.columns.values:
                if (value == 'title'):
                    data_columns_index.append('Title')
                elif (value == 'category'):
                    data_columns_index.append('Category')
                elif (value == 'source_url'):
                    data_columns_index.append('Source Url')
                elif (value == 'published_date'):
                    data_columns_index.append('Published')
                elif (value == 'summary'):
                    data_columns_index.append('Summary')
                elif (value == 'text_rank'):
                    data_columns_index.append('Text Rank')
                elif (value == 'word_count'):
                    data_columns_index.append('Word Count')
                elif (value == 'rank'):
                    data_columns_index.append('Rank')
            data_df.columns = data_columns_index

        session['page'] = 'Daily_News'
        session['page_data'] = json.dumps(data_df.to_json())
        session['group_name'] = group_name
        session['s_date'] = s_date
        session['e_date'] = e_date
        session['code'] = "---"

        data_shape = data_df.shape
        column_names = data_df.columns.values

        s_date = s_date.strftime("%Y-%m-%d")
        e_date = e_date.strftime("%Y-%m-%d")

        def get_news(offset=0, per_page=10):
            return data_df.iloc[offset: offset + per_page]

        total = len(data_df)
        page, per_page, offset = get_page_args(
            page_parameter='page', per_page_parameter='per_page')
        data_pagination = get_news(offset=offset, per_page=per_page)
        pagination = Pagination(
            page=page, per_page=per_page, total=total, css_framework='bootstrap4')

        return render_template('daily_news.html', tables=data_pagination, data_shape=data_shape,
                               column_names=column_names, page=page, per_page=per_page, pagination=pagination,
                               group=group_name, s_date=s_date, e_date=e_date, sites_daily=sites_daily,
                               username_login=username_login)

    else:
        limit = 0
        ascending = -1

        if 'page_data' in session:
            session.pop('group_name', None)
            session.pop('page_data', None)

        data_df = get_daily_news(group, s_date, e_date, limit, ascending)

        for news in data_df:
            try:
                news['text_rank'] = news['text_rank']
            except:
                news['text_rank'] = news['brief_content']

            news['summary'] = news['brief_content']
            b_content = news['brief_content']
            b_text_rank = news['text_rank']

            news['word_count'] = len(b_text_rank.split())
            try:
                b_content = b_content.split("\n")
                b_text_rank = b_text_rank.split("\n")
            except:
                b_content = "\n".join(b_content)
                b_content = b_content.split("\n")
                b_text_rank = "\n".join(b_text_rank)
                b_text_rank = b_text_rank.split("\n")

            b_content = [x.strip() for x in b_content]
            b_text_rank = [x.strip() for x in b_text_rank]

            n = 1
            for i, x in enumerate(b_content):
                check = re.match(url_regex, x)
                if check is not None:
                    if "vietstock" in x:
                        fname = x[x.rfind("/") + 1:]
                    else:
                        fname = "Tài liệu đính kèm {0}".format(n)
                    n += 1
                    b_content[i] = '<p><a class="text-blue-500" href="{0}" target="_blank">{1}</a></p>'.format(
                        x, fname)
            n = 1
            for i, x in enumerate(b_text_rank):
                check = re.match(url_regex, x)
                if check is not None:
                    if "vietstock" in x:
                        fname = x[x.rfind("/") + 1:]
                    else:
                        fname = "Tài liệu đính kèm {0}".format(n)
                    n += 1
                    b_text_rank[i] = '<p><a class="text-blue-500" href="{0}" target="_blank">{1}</a></p>'.format(
                        x, fname)

            del news['brief_content']
            news['summary'] = "<div class='content'>" + \
                              " ".join(b_content) + "</div>"
            news['text_rank'] = "<div class='content'>" + \
                                " ".join(b_text_rank) + "</div>"

        try:
            data_df = pd.DataFrame(data_df)
            data_df["rank"] = data_df["rank"].round(2)

            data_df.sort_values(by=["category", "rank", "reviewed", "published_date", "rank_score"],
                                inplace=True, ascending=[True, True, False, False, False])
            del data_df['rank_score']
            del data_df['reviewed']
        except:
            pass

        if (len(data_df) > 0):
            data_df['published_date'] = data_df['published_date'].dt.strftime(
                '%d/%m/%Y %H:%M')
            # del data_df['rank']
            data_columns_index = []
            for value in data_df.columns.values:
                if (value == 'title'):
                    data_columns_index.append('Title')
                elif (value == 'category'):
                    data_columns_index.append('Category')
                elif (value == 'source_url'):
                    data_columns_index.append('Source Url')
                elif (value == 'published_date'):
                    data_columns_index.append('Published')
                elif (value == 'summary'):
                    data_columns_index.append('Summary')
                elif (value == 'text_rank'):
                    data_columns_index.append('Text Rank')
                elif (value == 'word_count'):
                    data_columns_index.append('Word Count')
                elif (value == 'rank'):
                    data_columns_index.append('Rank')
            data_df.columns = data_columns_index

        session['page'] = 'Daily_News'
        session['page_data'] = json.dumps(data_df.to_json())
        session['group_name'] = group_name
        session['s_date'] = s_date
        session['e_date'] = e_date
        session['code'] = "---"

        data_shape = data_df.shape
        column_names = data_df.columns.values
        s_date = s_date.strftime("%Y-%m-%d")
        e_date = e_date.strftime("%Y-%m-%d")

        def get_news(offset=0, per_page=10):
            return data_df.iloc[offset: offset + per_page]

        total = len(data_df)
        page, per_page, offset = get_page_args(
            page_parameter='page', per_page_parameter='per_page')
        data_pagination = get_news(offset=offset, per_page=per_page)
        pagination = Pagination(
            page=page, per_page=per_page, total=total, css_framework='bootstrap4')

        return render_template('daily_news.html', tables=data_pagination, data_shape=data_shape,
                               column_names=column_names, page=page, per_page=per_page, pagination=pagination,
                               group=group_name, s_date=s_date, e_date=e_date, sites_daily=sites_daily,
                               username_login=username_login)


@routes.route("/daily_search", methods=["POST"])
def daily_search():
    if 'user_name' not in session:
        return redirect('/login')

    username_login = session['user_name']

    try:
        search_keyword = request.form['search_keyword']
        search_keyword = nl('NFKC', search_keyword)

        d = datetime.today() - timedelta(days=14)
        s_date = datetime.strptime(d.strftime(
            "%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M")
        e_date = datetime.strptime(
            datetime.today().strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M")
    except:
        return

    if search_keyword is None:
        return
    if len(search_keyword) == 0:
        return

    limit = 0
    ascending = -1
    data_df = get_data_by_content_and_keyword(
        search_keyword, s_date, e_date, limit, ascending)

    for news in data_df:
        try:
            news['stock_code'] = news['stock_code']
        except:
            news['stock_code'] = "---"

        try:
            news['text_rank'] = news['text_rank']
        except:
            news['text_rank'] = news['brief_content']

        b_content = news['brief_content']
        b_text_rank = news['text_rank']

        news['word_count'] = len(b_text_rank.split())
        try:
            b_content = b_content.split("\n")
            b_text_rank = b_text_rank.split("\n")
        except:
            b_content = "\n".join(b_content)
            b_content = b_content.split("\n")
            b_text_rank = "\n".join(b_text_rank)
            b_text_rank = b_text_rank.split("\n")

        b_content = [x.strip() for x in b_content]
        b_text_rank = [x.strip() for x in b_text_rank]

        n = 1
        for i, x in enumerate(b_content):
            check = re.match(url_regex, x)
            if check is not None:
                if "vietstock" in x:
                    fname = x[x.rfind("/") + 1:]
                else:
                    fname = "Tài liệu đính kèm {0}".format(n)
                n += 1
                b_content[i] = '<p><a class="text-blue-500" href="{0}" target="_blank">{1}</a></p>'.format(
                    x, fname)
        n = 1
        for i, x in enumerate(b_text_rank):
            check = re.match(url_regex, x)
            if check is not None:
                if "vietstock" in x:
                    fname = x[x.rfind("/") + 1:]
                else:
                    fname = "Tài liệu đính kèm {0}".format(n)
                n += 1
                b_text_rank[i] = '<p><a class="text-blue-500" href="{0}" target="_blank">{1}</a></p>'.format(
                    x, fname)

        del news['brief_content']
        news['summary'] = "<div class='content'>" + \
                          " ".join(b_content) + "</div>"
        news['text_rank'] = "<div class='content'>" + \
                            " ".join(b_text_rank) + "</div>"

    try:
        data_df = pd.DataFrame(data_df)
        data_df["rank"] = data_df["rank"].round(2)

        data_df.sort_values(by=["category", "rank", "reviewed", "published_date", "rank_score"],
                            inplace=True, ascending=[True, True, False, False, False])
        del data_df['rank_score']
        del data_df['reviewed']
    except:
        pass

    if (len(data_df) > 0):
        data_df['published_date'] = data_df['published_date'].dt.strftime(
            '%d/%m/%Y %H:%M')
        # del data_df['rank']
        data_columns_index = []
        for value in data_df.columns.values:
            if (value == 'title'):
                data_columns_index.append('Title')
            elif (value == 'category'):
                data_columns_index.append('Category')
            elif (value == 'source_url'):
                data_columns_index.append('Source Url')
            elif (value == 'published_date'):
                data_columns_index.append('Published')
            elif (value == 'stock_code'):
                data_columns_index.append('Stock Code')
            elif (value == 'summary'):
                data_columns_index.append('Summary')
            elif (value == 'text_rank'):
                data_columns_index.append('Text Rank')
            elif (value == 'word_count'):
                data_columns_index.append('Word Count')
            elif (value == 'rank'):
                data_columns_index.append('Rank')
        data_df.columns = data_columns_index

    session['page'] = 'Daily_Search'
    session['page_data'] = json.dumps(data_df.to_json())
    session['group_name'] = None
    session['s_date'] = s_date
    session['e_date'] = e_date
    session['code'] = '---'

    data_shape = data_df.shape
    column_names = data_df.columns.values
    s_date = s_date.strftime("%Y-%m-%d")
    e_date = e_date.strftime("%Y-%m-%d")

    def get_news(offset=0, per_page=10):
        return data_df.iloc[offset: offset + per_page]

    total = len(data_df)
    page, per_page, offset = get_page_args(
        page_parameter='page', per_page_parameter='per_page')
    data_pagination = get_news(offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page,
                            total=total, css_framework='bootstrap4')

    return render_template('daily_news.html', tables=data_pagination, data_shape=data_shape,
                           column_names=column_names, page=page, per_page=per_page, pagination=pagination,
                           group=None, s_date=s_date, e_date=e_date, sites_daily=sites_daily,
                           username_login=username_login)


@routes.route("/daily_search", methods=["GET"])
def daily_search_get():
    if 'user_name' not in session:
        return redirect('/login')

    username_login = session['user_name']
    data_df = pd.read_json(json.loads(session['page_data']))
    group_name = session['group_name']
    s_date = session['s_date']
    e_date = session['e_date']
    data_shape = data_df.shape
    column_names = data_df.columns.values
    s_date = s_date.strftime("%Y-%m-%d")
    e_date = e_date.strftime("%Y-%m-%d")

    def get_news(offset=0, per_page=10):
        return data_df.iloc[offset: offset + per_page]

    total = len(data_df)
    page, per_page, offset = get_page_args(
        page_parameter='page', per_page_parameter='per_page')
    data_pagination = get_news(offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page,
                            total=total, css_framework='bootstrap4')

    return render_template('daily_news.html', tables=data_pagination, data_shape=data_shape,
                           column_names=column_names, page=page, per_page=per_page, pagination=pagination,
                           group=group_name, s_date=s_date, e_date=e_date, sites_daily=sites_daily,
                           username_login=username_login)
