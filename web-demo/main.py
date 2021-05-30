#!/home/ubuntu/anaconda3/envs/ainews/bin/python
from flask_session import Session
from routes import *
from helpers import *
from flask import Flask, request, send_file
from io import BytesIO
from bs4 import BeautifulSoup
import bs4

sess = Session()
app = Flask(__name__)
app.config.from_object('config.Config')

sess.init_app(app)

top_daily_news = {
}

top_morning_news = {
}

six_news = {
}

with app.app_context():
    app.register_blueprint(routes)


    @app.route("/", methods=['POST', 'GET'])
    def home():
        if 'user_name' not in session:
            return redirect('/login')

        username_login = session['user_name']

        today = datetime.now(pytz.timezone(
            'Asia/Bangkok'))
        yesterday = datetime.now(pytz.timezone('Asia/Bangkok')) - timedelta(1)
        if today.hour >= 8:
            s_date = datetime.strptime(yesterday.strftime(
                "%Y-%m-%d" + " 08:01"), "%Y-%m-%d %H:%M")
            e_date = datetime.strptime(today.strftime("%Y-%m-%d") + " 08:00", "%Y-%m-%d %H:%M")
        else:
            today = today - timedelta(1)
            yesterday = yesterday - timedelta(1)
            s_date = datetime.strptime(yesterday.strftime(
                "%Y-%m-%d" + " 08:01"), "%Y-%m-%d %H:%M")
            e_date = datetime.strptime(today.strftime("%Y-%m-%d") + " 08:00", "%Y-%m-%d %H:%M")
        data_df = get_daily_news_main(None, s_date, e_date, 0, -1)

        for news in data_df:
            try:
                news['text_rank'] = news['text_rank']
            except:
                news['text_rank'] = news['brief_content']
            if "reviewed" not in news.keys():
                news['reviewed'] = 0

        data_df = pd.DataFrame(data_df)
        if len(data_df) > 0:
            try:
                data_df.sort_values(
                    by=["rank", "rank_score", "reviewed"], inplace=True, ascending=[True, False, False])
            except:
                data_df.sort_values(
                    by=["rank", "rank_score"], inplace=True, ascending=[True, False])

        try:
            top_daily_news["Macro news"] = data_df[data_df.category ==
                                                   "macro_news"].iloc[0]
        except:
            pass
        try:
            top_daily_news["International news"] = data_df[data_df.category ==
                                                           "international_news"].iloc[0]
        except:
            pass
        try:
            top_daily_news["Stock market news"] = data_df[data_df.category ==
                                                          "stock_market"].iloc[0]
        except:
            pass

        # six news
        today = datetime.now(pytz.timezone(
            'Asia/Bangkok'))
        if today.hour >= 8 and today.hour < 15:
            yesterday = datetime.now(pytz.timezone('Asia/Bangkok')) - timedelta(1)
            e_date = datetime.strptime(today.strftime(
                "%Y-%m-%d") + " 08:00", "%Y-%m-%d %H:%M")
            s_date = datetime.strptime(yesterday.strftime("%Y-%m-%d") + " 16:00", "%Y-%m-%d %H:%M")
        else:
            if today.hour < 8:
                today = today - timedelta(1)
            s_date = datetime.strptime(today.strftime(
                "%Y-%m-%d") + " 08:00", "%Y-%m-%d %H:%M")
            e_date = datetime.strptime(today.strftime(
                "%Y-%m-%d") + " 16:00", "%Y-%m-%d %H:%M")

        # yesterday = datetime.now(pytz.timezone('Asia/Bangkok')) - timedelta(1)
        # s_date = datetime.strptime(yesterday.strftime(
        #     "%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M")
        # e_date = datetime.strptime(today, "%Y-%m-%d %H:%M")
        print(s_date, e_date)
        data_df = get_daily_news_main(None, s_date, e_date, 0, -1)

        for news in data_df:
            try:
                news['text_rank'] = news['text_rank']
            except:
                news['text_rank'] = news['brief_content']
            if "reviewed" not in news.keys():
                news['reviewed'] = 0

        data_df = pd.DataFrame(data_df)
        if len(data_df) > 0:
            try:
                data_df.sort_values(
                    by=["rank", "rank_score", "reviewed"], inplace=True, ascending=[True, False, False])
            except:
                data_df.sort_values(
                    by=["rank", "rank_score"], inplace=True, ascending=[True, False])

        try:
            for i in range(min(3, len(data_df[data_df.category == "macro_news"]))):
                six_news["Macro news {0}".format(i + 1)] = data_df[data_df.category ==
                                                                   "macro_news"].iloc[i]
        except:
            pass
        try:
            for i in range(min(3, len(data_df[data_df.category == "international_news"]))):
                six_news["International news {0}".format(i + 1)] = data_df[data_df.category ==
                                                                           "international_news"].iloc[i]
        except:
            pass

        # s_date = datetime.strptime(yesterday.strftime(
        #     "%Y-%m-%d") + " 00:00", "%Y-%m-%d %H:%M")
        today = datetime.now(pytz.timezone(
            'Asia/Bangkok'))
        yesterday = today - timedelta(1)
        if today.hour < 15:
            today = today - timedelta(1)
            yesterday = yesterday - timedelta(1)
        s_date = datetime.strptime(yesterday.strftime(
            "%Y-%m-%d" + " 16:00"), "%Y-%m-%d %H:%M")
        e_date = datetime.strptime(today.strftime("%Y-%m-%d") + " 16:00", "%Y-%m-%d %H:%M")
        print("===>", s_date, e_date)
        data_df = get_morning_news_main(s_date, e_date, 0, -1)

        for news in data_df:
            try:
                news['text_rank'] = news['text_rank']
            except:
                news['text_rank'] = news['brief_content']
            if re.findall(url_regex, news['brief_content']):
                news['text_rank'] = news['brief_content']
            if "reviewed" not in news.keys():
                news['reviewed'] = 0
            b_content = news['text_rank']
            # print(b_content)
            try:
                b_content = b_content.split("\n")
            except:
                b_content = "\n".join(b_content)
                b_content = b_content.split("\n")

            b_content = [x.strip() for x in b_content]

            n = 1
            word_count = len(b_content[0].split())
            # print(b_content)
            remove_ids = []
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
                else:
                    if word_count + len(x.split()) <= 60:
                        word_count += len(x.split())
                    else:
                        if i > 0:
                            remove_ids.append(i)
            # print(remove_ids)
            remove_ids.reverse()
            for i in remove_ids:
                del b_content[i]

            news['text_rank'] = "<div class='content bg-gray-100 text-md px-5 py-3'>" + \
                                " ".join(b_content) + "</div>"

        data_df = pd.DataFrame(data_df)
        if len(data_df) > 0:
            try:
                data_df.sort_values(
                    by=["rank", "rank_score", "reviewed"], inplace=True, ascending=[True, False, False])
            except:
                data_df.sort_values(by=["rank", "rank_score"], inplace=True, ascending=[True, False])

        urls = []
        try:
            c = 0
            titles = []
            codes = []
            l_news = data_df[data_df.category == "banking"]
            for i in range(0, len(l_news)):
                news = l_news.iloc[i]
                if news['source_url'] in urls:
                    continue
                if news['title'].lower().strip() not in titles and news['stock_code'] not in codes:
                    codes.append(news['stock_code'])
                    c += 1
                    titles.append(news['title'].lower().strip())
                    top_morning_news["Banking {0}".format(c)] = news
                    codes.append(news['stock_code'])
                    urls.append(news['source_url'])
                if c >= 4:
                    break
        except Exception as ex:
            print(ex)
            pass
        try:
            c = 0
            titles = []
            codes = []
            l_news = data_df[data_df.category == "real_estate"]
            for i in range(0, len(l_news)):
                news = l_news.iloc[i]
                if news['source_url'] in urls:
                    continue
                check = True
                for title in titles:
                    if news['title'].lower().strip() in title or title in news['title'].lower().strip():
                        check = False
                        break
                if check and news['stock_code'] not in codes:
                    codes.append(news['stock_code'])
                    c += 1
                    titles.append(news['title'].lower().strip())
                    top_morning_news["Real estate {0}".format(c)] = news
                    urls.append(news['source_url'])
                if c >= 2:
                    break
        except:
            pass
        try:
            cat_news = data_df[data_df.category == "vingroup"]
            i = 0
            while i < len(cat_news):
                news = cat_news.iloc[i]
                if news['source_url'] in urls:
                    i += 1
                    continue
                top_morning_news["Vingroup"] = news
                urls.append(news['source_url'])
                break
        except:
            pass
        try:
            cat_news = data_df[data_df.category == "oil_and_gas"]
            # print(cat_news)
            i = 0
            while i < len(cat_news):
                news = cat_news.iloc[i]
                if news['source_url'] in urls:
                    i += 1
                    continue
                top_morning_news["Oil and Gas"] = news
                urls.append(news['source_url'])
                break
        except:
            pass
        try:
            c = 0
            titles = []
            codes = []
            l_news = data_df[data_df.category == "food_and_drink"]
            for i in range(0, len(l_news)):
                news = l_news.iloc[i]
                if news['source_url'] in urls:
                    continue
                check = True
                for title in titles:
                    if news['title'].lower().strip() in title or title in news['title'].lower().strip():
                        check = False
                        break
                if check and news['stock_code'] not in codes:
                    codes.append(news['stock_code'])
                    c += 1
                    titles.append(news['title'].lower().strip())
                    top_morning_news["Food and Drink {0}".format(c)] = news
                    urls.append(news['source_url'])
                if c >= 2:
                    break
        except:
            pass
        try:
            c = 0
            titles = []
            codes = []
            l_news = data_df[data_df.category == "others"]
            for i in range(0, len(l_news)):
                news = l_news.iloc[i]
                if news['source_url'] in urls:
                    continue
                check = True
                for title in titles:
                    if news['title'].lower().strip() in title or title in news['title'].lower().strip():
                        check = False
                        break
                if check and news['stock_code'] not in codes:
                    codes.append(news['stock_code'])
                    c += 1
                    titles.append(news['title'].lower().strip())
                    top_morning_news["Others {0}".format(c)] = news
                    urls.append(news['source_url'])
                if c >= 3:
                    break
        except:
            pass

        # print(top_morning_news)

        return render_template('main.html', username_login=username_login, top_daily_news=top_daily_news, six_news=six_news,
                               top_morning_news=top_morning_news)


    @app.route("/export_excel", methods=['POST', 'GET'])
    def export_excel():
        if 'user_name' not in session:
            return redirect('/login')

        page = session['page']
        group_name = session['group_name']
        code = session['code']
        if group_name is None:
            group_name = "All"
        data_df = pd.read_json(json.loads(session['page_data']))
        for idx, row in data_df.iterrows():
            soup = BeautifulSoup(row['Summary'])
            result = ""
            for t in soup.find("div", {"class": "content"}).contents:
                if type(t) != bs4.element.Tag:
                    result = result + "\n" + t
                else:
                    result = result + "\n" + t.find('a', href=True)['href']
            data_df.at[idx, 'Summary'] = result.strip()
            soup = BeautifulSoup(row['Text Rank'])
            result = ""
            for t in soup.find("div", {"class": "content"}).contents:
                if type(t) != bs4.element.Tag:
                    result = result + "\n" + t
                else:
                    result = result + "\n" + t.find('a', href=True)['href']
            data_df.at[idx, 'Text Rank'] = result.strip()

        data_df.rename(columns={'Summary': "Brief Content"}, inplace=True)
        data_df.rename(
            columns={'Text Rank': "Extractive Summary"}, inplace=True)
        s_date = session['s_date']
        e_date = session['e_date']

        s_date = s_date.strftime("%Y-%m-%d")
        e_date = e_date.strftime("%Y-%m-%d")
        if (code == '---'):
            filename = str(page) + '-' + str(group_name) + '-' + str(s_date) + \
                       '-' + str(e_date) + '.xlsx'
        else:
            filename = str(page) + '-' + str(group_name) + '-' + str(code) + '-' + str(s_date) + \
                       '-' + str(e_date) + '.xlsx'
        in_memory_fp = BytesIO()
        data_df.to_excel(in_memory_fp)
        in_memory_fp.seek(0)
        return send_file(in_memory_fp, attachment_filename=filename, as_attachment=True)


    @app.route("/export_word", methods=['POST', 'GET'])
    def export_word():
        filename = "ImportantNews_{0}.docx".format(datetime.now(
            pytz.timezone('Asia/Bangkok')).strftime("%d-%m-%Y"))
        print(filename)
        doc = write_docx(top_daily_news, top_morning_news, six_news, datetime.now(
            pytz.timezone('Asia/Bangkok')).strftime("%d-%m-%Y"))
        return send_file(doc, attachment_filename=filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
