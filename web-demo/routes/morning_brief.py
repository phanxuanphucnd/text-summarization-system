from helpers import *
from config import *
from . import routes

import pandas as pd
from datetime import datetime, timedelta
import os
import re
import json
import pytz
from flask import render_template, session, redirect, request
from flask_paginate import Pagination, get_page_args
from unicodedata import normalize as nl


@routes.route("/morning_brief", methods=['GET'])
def morning_brief_get():
    if 'user_name' not in session:
        return redirect('/login')

    username_login = session['user_name']

    today = datetime.now(pytz.timezone('Asia/Bangkok')).strftime("%Y-%m-%d")
    yesterday = datetime.now(pytz.timezone('Asia/Bangkok')) - timedelta(1)
    s_date = datetime.strptime(yesterday.strftime(
        "%Y-%m-%d") + " 00:00", "%Y-%m-%d %H:%M")
    e_date = datetime.strptime(today + " 23:59", "%Y-%m-%d %H:%M")
    group_name = None
    code = None

    if request.args.get('page') is None:
        if 'page_data' in session:
            session.pop('page_data', None)
            session.pop('group_name', None)
    limit = 0
    ascending = -1

    if 'page_data' in session:
        data_df = pd.read_json(json.loads(session['page_data']))
        group_name = session['group_name']
        if group_name is None:
            group_name = "Select a group"
        s_date = session['s_date']
        e_date = session['e_date']
        code = session['code']
        data_shape = data_df.shape
        column_names = data_df.columns.values

        def get_news(offset=0, per_page=10):
            return data_df.iloc[offset: offset + per_page]

        total = len(data_df)
        page, per_page, offset = get_page_args(
            page_parameter='page', per_page_parameter='per_page')
        data_pagination = get_news(offset=offset, per_page=per_page)
        pagination = Pagination(
            page=page, per_page=per_page, total=total, css_framework='bootstrap4')

        s_date = s_date.strftime("%Y-%m-%d")
        e_date = e_date.strftime("%Y-%m-%d")

        print(group_name, code, s_date, e_date)

        return render_template('morning_brief.html', tables=data_pagination, data_shape=data_shape,
                               column_names=column_names, page=page, per_page=per_page,
                               pagination=pagination, group=group_name, s_date=s_date, e_date=e_date, code=code,
                               sites_morning=sites_morning, stock_map_morning=stock_map_morning,
                               username_login=username_login)
    else:
        data_df = get_morning_news(s_date, e_date, limit, ascending)

        for news in data_df:
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
                    b_text_rank.pop(i)

            del news['brief_content']
            news['summary'] = "<div class='content'>" + \
                              " ".join(b_content) + "</div>"
            news['text_rank'] = "<div class='content'>" + \
                                " ".join(b_text_rank) + "</div>"

        # try:
        data_df = pd.DataFrame(data_df)
        data_df["rank"] = data_df["rank"].round(2)

        data_df.sort_values(by=["category", "rank", "reviewed", "published_date", "rank_score"],
                            inplace=True, ascending=[True, True, False, False, False])
        del data_df['rank_score']
        del data_df['reviewed']
        # except:
        #     pass

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

        session['page'] = 'Morning_Brief'
        session['page_data'] = json.dumps(data_df.to_json())
        session['group_name'] = None
        session['s_date'] = s_date
        session['e_date'] = e_date
        if code is None:
            session['code'] = '---'
        else:
            session['code'] = code

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

        return render_template('morning_brief.html', tables=data_pagination, data_shape=data_shape,
                               column_names=column_names, page=page, per_page=per_page,
                               pagination=pagination, group=group_name, s_date=s_date, e_date=e_date, code=code,
                               sites_morning=sites_morning, stock_map_morning=stock_map_morning,
                               username_login=username_login)


@routes.route("/morning_brief", methods=['POST'])
def morning_brief_post():
    if 'user_name' not in session:
        return redirect('/login')

    username_login = session['user_name']

    today = datetime.now(pytz.timezone('Asia/Bangkok')).strftime("%Y-%m-%d")
    try:
        group = request.form["site"]
        group_name = group
        group = group_map_morning[group]
    except:
        group = None
        group_name = None
    try:
        code = request.form['stock-code']
    except:
        code = None
    try:
        s_date = request.form['search_start_dates']
        s_date = datetime.strptime(s_date + " 00:00", "%Y-%m-%d %H:%M")
    except:
        s_date = datetime.strptime(today + " 00:00", "%Y-%m-%d %H:%M")
    try:
        e_date = request.form['search_end_dates']
        e_date = datetime.strptime(e_date + " 23:59", "%Y-%m-%d %H:%M")
    except:
        e_date = datetime.strptime(today + " 00:00", "%Y-%m-%d %H:%M")

    if group is None:
        limit = 0
        ascending = -1

        if 'page_data' in session:
            session.pop('group_name', None)
            session.pop('page_data', None)

        data_df = get_morning_news(s_date, e_date, limit, ascending)

        for news in data_df:
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
                    b_text_rank.pop(i)

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

        session['page'] = 'Morning_Brief'
        session['page_data'] = json.dumps(data_df.to_json())
        session['group_name'] = None
        session['s_date'] = s_date
        session['e_date'] = e_date
        if code is None:
            session['code'] = '---'
        else:
            session['code'] = code

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

        return render_template('morning_brief.html', tables=data_pagination, data_shape=data_shape,
                               column_names=column_names, page=page, per_page=per_page,
                               pagination=pagination, group=group_name, s_date=s_date, e_date=e_date, code=code,
                               sites_morning=sites_morning, stock_map_morning=stock_map_morning,
                               username_login=username_login)
    else:
        limit = 0
        ascending = -1
        data_df = get_data_by_category_and_date(
            group, s_date, e_date, code, limit, ascending)

        # print(data_df)

        for news in data_df:
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
                    b_text_rank.pop(i)

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

        session['page'] = 'Morning_Brief'
        session['page_data'] = json.dumps(data_df.to_json())
        session['group_name'] = group_name
        session['s_date'] = s_date
        session['e_date'] = e_date
        if code is None:
            session['code'] = '---'
        else:
            session['code'] = code

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

        return render_template('morning_brief.html', tables=data_pagination, data_shape=data_shape,
                               column_names=column_names, page=page, per_page=per_page,
                               pagination=pagination, group=group_name, s_date=s_date, e_date=e_date, code=code,
                               sites_morning=sites_morning, stock_map_morning=stock_map_morning,
                               username_login=username_login)


@routes.route("/morning_search", methods=["POST"])
def morning_search():
    if 'user_name' not in session:
        return redirect('/login')

    username_login = session['user_name']

    today = datetime.now(pytz.timezone('Asia/Bangkok'))
    group_name = None
    code = None

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

    if search_keyword is None or len(search_keyword) == 0:
        s_date, e_date = today, today
        data_shape = (0, 0)
        column_names = []
        page, per_page, offset = 0, 0, 0
        pagination, data_pagination = None, None

        s_date = s_date.strftime("%Y-%m-%d")
        e_date = e_date.strftime("%Y-%m-%d")

        return render_template('morning_brief.html', tables=data_pagination, data_shape=data_shape,
                               column_names=column_names, page=page, per_page=per_page,
                               pagination=pagination, group=group_name, s_date=s_date, e_date=e_date, code=code,
                               sites_morning=sites_morning, stock_map_morning=stock_map_morning,
                               username_login=username_login)

    if 'page_data' in session:
        session.pop('page_data', None)
        session.pop('group_name', None)
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
                b_text_rank.pop(i)

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

    session['page'] = 'Morning_Search'
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

    return render_template('morning_brief.html', tables=data_pagination, data_shape=data_shape,
                           column_names=column_names, page=page, per_page=per_page,
                           pagination=pagination, group=None, s_date=s_date, e_date=e_date, code=None,
                           sites_morning=sites_morning, stock_map_morning=stock_map_morning,
                           username_login=username_login)


@routes.route("/morning_search", methods=["GET"])
def morning_search_get():
    if 'user_name' not in session:
        return redirect('/login')

    username_login = session['user_name']
    data_df = pd.read_json(json.loads(session['page_data']))
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

    return render_template('morning_brief.html', tables=data_pagination, data_shape=data_shape,
                           column_names=column_names, page=page, per_page=per_page,
                           pagination=pagination, group=None, s_date=s_date, e_date=e_date, code=None,
                           sites_morning=sites_morning, stock_map_morning=stock_map_morning,
                           username_login=username_login)


@routes.route("/update", methods=["POST"])
def update():
    if 'user_name' not in session:
        return redirect('/login')

    df = pd.read_json(json.loads(session['page_data']))

    url = request.form['url']
    url = nl('NFKC', url)
    category = request.form['category']
    category = nl('NFKC', category)
    old_cat = request.form['old_category']
    old_cat = nl('NFKC', old_cat)
    text_rank = request.form['text_rank']
    text_rank = nl('NFKC', text_rank)

    try:
        update_news({"source_url": url, "category": old_cat}, {
            "$set": {"category": category, "text_rank": text_rank,
                     "reviewed": datetime.now(pytz.timezone('Asia/Bangkok')).timestamp()}})
        text_rank = "<div class='content'>" + text_rank + "</div>"
        df.loc[df['Source Url'] == url, ["Category", "Text Rank"]] = [
            category, text_rank]
        session['page_data'] = json.dumps(df.to_json())
    except Exception as ex:
        print(ex)
        pass
    return "ok"


@routes.route("/set_top", methods=["GET"])
def set_top():
    url = request.args.get('url')
    cat = request.args.get('category')
    url = nl('NFKC', url)
    callback = request.args.get("callback")
    callback = nl('NFKC', callback)
    # print(callback)
    published_date = None
    if callback.strip() == 'morning_brief':
        today = datetime.now(pytz.timezone('Asia/Bangkok'))
        published_date = today - timedelta(hours=today.hour) + timedelta(hours=17)
        # print(published_date)

    if published_date is not None:
        update_news({"source_url": url, "category": cat},
                    {"$set": {"rank": 1, "rank_score": 10000, "published_date": published_date, "reviewed": datetime.now(
                        pytz.timezone('Asia/Bangkok')).timestamp()}})
    else:
        update_news({"source_url": url, "category": cat},
                    {"$set": {"rank": 1, "rank_score": 10000, "reviewed": datetime.now(
                        pytz.timezone('Asia/Bangkok')).timestamp()}})
    return redirect(callback)


@routes.route("/six_news", methods=["GET"])
def six_news():
    url = request.args.get('url')
    cat = request.args.get('category')
    url = nl('NFKC', url)
    callback = request.args.get("callback")
    callback = nl('NFKC', callback)

    today = datetime.now(pytz.timezone('Asia/Bangkok'))
    # print(today)
    if today.hour >= 16:
        published_date = today - timedelta(hours=today.hour) + timedelta(hours=17)
    if today.hour < 16:
        published_date = today - timedelta(hours=today.hour) + timedelta(hours=12)
    # print(published_date)
    yesterday = today - timedelta(1)
    s_date = datetime.strptime(yesterday.strftime(
        "%Y-%m-%d") + " 00:00", "%Y-%m-%d %H:%M")
    e_date = datetime.strptime(today.strftime("%Y-%m-%d") + " 23:59", "%Y-%m-%d %H:%M")

    rank_score = get_max_rank(s_date, e_date, cat) - 0.00001

    update_news({"source_url": url, "category": cat}, {
        "$set": {"rank": 1, "published_date": published_date, "rank_score": rank_score, "reviewed": datetime.now(
            pytz.timezone('Asia/Bangkok')).timestamp()}})
    return redirect(callback)
