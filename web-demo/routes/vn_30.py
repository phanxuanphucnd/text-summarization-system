from . import routes
import json
from flask import render_template, session, redirect, request
import requests
import os
from unicodedata import normalize as nl

DIR = "../news_system/crawler/scraper/vn30"


def get_vn30():
    vn30_news = []
    stock_code_list = []
    mapping = {}

    r = requests.get(
        "https://www.hsx.vn/Modules/Listed/Web/StockIndex/1964531007?_search=false&nd=1612005640891&rows=2147483647"
        "&page=1&sidx=id&sord=desc")
    data = r.json()

    for row in data['rows']:
        if row['cell'][2].strip() not in stock_code_list:
            vn30_news.append(
                {"stock_code": row['cell'][2].strip(), "company_name": row['cell'][5].strip()})
            mapping[row['cell'][2].strip().upper()] = row['cell'][5].strip()
            stock_code_list.append(row['cell'][2].strip().upper())

    categories = ['banking', 'food_and_drink',
                  'oil_and_gas', 'others', 'real_estate', 'vingroup']
    vn30_list = json.load(open('vn30.json', mode='r'))
    return vn30_news, stock_code_list, mapping, vn30_list, categories


@routes.route("/vn_30", methods=["GET"])
def vn_30_get():
    if 'user_name' not in session:
        return redirect('/login')

    username_login = session['user_name']

    vn30_news, stock_code_list, mapping, vn30_list, categories = get_vn30()

    for c in vn30_list:
        if c['code'].upper() not in stock_code_list:
            vn30_list.remove(c)

    old_code_list = [x['code'] for x in vn30_list]
    for new_c in stock_code_list:
        if new_c not in old_code_list:
            vn30_list.append({"code": new_c, "group": "others"})

    for c in vn30_list:
        c['company_name'] = mapping[c['code']]

    vn30 = sorted(vn30_list, key=lambda k: k['group'])
    session['vn30_list'] = vn30

    return render_template('vn_30.html', vn30=vn30, no_stock=len(vn30), categories=categories, username_login=username_login)


@routes.route("/vn30_change_group", methods=['POST'])
def vn30_change_group():
    code = request.form['code']
    code = nl('NFKC', code)
    group = request.form['group']
    group = nl('NFKC', group)

    for c in session['vn30_list']:
        if c['code'].strip().upper() == code.strip().upper():
            c['group'] = group
            return "change success"
    return "can't find"


@routes.route("/vn30_save", methods=['POST'])
def vn30_save():
    vn30 = session['vn30_list']
    print(vn30)
    json.dump(vn30, open('vn30.json', mode="w"))
    vn30 = sorted(vn30, key=lambda k: k['group'])
    l = []
    g = "None"
    for i, c in enumerate(vn30):
        if c['group'] != g:
            if len(l) == 0:
                l.append(c)
                g = c['group']
                continue
            data = []
            if len(l) > 5:
                data.append(l[:len(l) // 2])
                data.append(l[len(l) // 2:])
            else:
                data.append(l)

            for i, d in enumerate(data):
                fname = os.path.join(DIR, "{0}_{1}.json".format(g, i + 1))
                json.dump(d, open(fname, mode="w"))
            l = []
            l.append(c)
        else:
            l.append(c)
        g = c['group']
    data = []
    if len(l) > 5:
        data.append(l[:len(l) // 2])
        data.append(l[len(l) // 2:])
    else:
        data.append(l)

    for i, d in enumerate(data):
        fname = os.path.join(DIR, "{0}_{1}.json".format(g, i + 1))
        json.dump(d, open(fname, mode="w"))
    return redirect("/vn_30")
