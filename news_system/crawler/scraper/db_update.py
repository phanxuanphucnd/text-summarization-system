"""
Testing
"""

from summarizer import Summarizer
import pymongo
#from sshtunnel import SSHTunnelForwarder
#import paramiko
import io
#import base64

#with open('AIapp.pem', 'rb') as f:
#    blob = base64.b64encode(f.read())

#SSH_KEY_BLOB = blob  # .decode('utf-8')

# decode key back into a useable form from base64
#SSH_KEY_BLOB_DECODED = base64.b64decode(SSH_KEY_BLOB)
#SSH_KEY = SSH_KEY_BLOB_DECODED.decode('utf-8')

# pass key to parmiko to get your pkey
#pkey = paramiko.RSAKey.from_private_key(io.StringIO(SSH_KEY))

#MONGO_HOST = "18.136.12.76"
MONGO_DB = "news_db"
MONGO_USER = "aiteam"
MONGO_PASS = "aiteam123"

#server = SSHTunnelForwarder(
#    MONGO_HOST,
#    remote_bind_address=('127.0.0.1', 27017),
#    ssh_username='ubuntu',
#    ssh_pkey=pkey
#)

#server.start()
client = pymongo.MongoClient('127.0.0.1', 27017, username=MONGO_USER, password=MONGO_PASS,
                             authSource='admin')
db = client[MONGO_DB]

summarizer = Summarizer(
    model='vinai/phobert-base',
    hidden=-2,
    reduce_option='mean'
)


from classifier import Classifier

classifier_daily = Classifier(model_path="./classifier/models/dailynews_best.model")
classifier_morning = Classifier(model_path="./classifier/models/morning_brief_best.model")


from summarizer.ViTextRank import ViTextRank
text_rank = ViTextRank()

from datetime import datetime

s_date = datetime.strptime("2020-12-12" + " 00:00", "%Y-%m-%d %H:%M")
e_date = datetime.strptime("2021-01-12" + " 23:59", "%Y-%m-%d %H:%M")

for obj in db.news_tbl.find({"category": {"$in": ["macro_news"]}, "published_date": {"$lt": e_date, "$gte": s_date}}).limit(5000):
    try:
        brief = obj['brief_content']
        try:
            content = obj['content']
            if brief not in content or content not in brief:
                content = content + "\n" + brief
            id = obj['_id']
            if 'content' not in obj.keys() or 'brief_content' not in obj.keys():
                print(obj)
                continue

            try:
                summarization = summarizer(content, ratio=0.2, max_words=-1)
                print("==> cluster:", summarization)
            except:
                summarization = brief
        except:
            summarization = obj['brief_content']
            print("???")
        if len(summarization) == 0:
            summarization = obj['brief_content']

        try:
            item['text_rank'] = text_rank.run(content, ratio=0.2, max_words=-1)
            print("==> textrank:", item['text_rank'])
        except:
            item['text_rank'] = item['brief_content']
            print("???")
        try:
            db.news_tbl.update_one({"_id": id}, {"$set": {"summary": summarization}})
        except Exception as ex:
            print(obj["source_url"])
    except:
        pass
    try:
        doc_to_classify = obj['title'] + "\n" + obj['brief_content']
        label = classifier_daily.predict(sample=doc_to_classify)
        id = obj['_id']
        db.news_tbl.update_one({"_id": id}, {"$set": {"category": label['class'], "score": str(label['score'])}})
    except Exception as ex:
        print(obj["source_url"])


for obj in db.news_tbl.find({"category": {"$in": ["international_news"]}, "published_date": {"$lt": e_date, "$gte": s_date}}).limit(5000):
    try:
        brief = obj['brief_content']
        try:
            content = obj['content']
            if brief not in content or content not in brief:
                content = content + "\n" + brief

            id = obj['_id']
            if 'content' not in obj.keys() or 'brief_content' not in obj.keys():
                print(obj)
                continue

            try:
                summarization = summarizer(content, ratio=0.2, max_words=-1)
                print("==>", summarization)
            except:
                print("----->", obj["source_url"])
                summarization = brief
        except:
            summarization = obj['brief_content']
        if len(summarization) == 0:
            summarization = obj['brief_content']
        try:
            item['text_rank'] = text_rank.run(content, ratio=0.2, max_words=-1)
            print("==> textrank:", item['text_rank'])
        except:
            item['text_rank'] = item['brief_content']

        try:
            db.news_tbl.update_one({"_id": id}, {"$set": {"summary": summarization}})
        except Exception as ex:
            print(obj["source_url"])
    except:
        pass
    try:
        doc_to_classify = obj['title'] + "\n" + obj['brief_content']
        label = classifier_daily.predict(sample=doc_to_classify)
        id = obj['_id']
        db.news_tbl.update_one({"_id": id}, {"$set": {"category": label['class'], "score": str(label['score'])}})
    except Exception as ex:
        print(obj["source_url"])



for obj in db.news_tbl.find({"category": {"$in": ["stock_market"]}, "published_date": {"$lt": e_date, "$gte": s_date}}).limit(5000):
    try:
        brief = obj['brief_content']
        try:
            content = obj['content']
            if brief not in content or content not in brief:
                content = content + "\n" + brief

            id = obj['_id']
            if 'content' not in obj.keys() or 'brief_content' not in obj.keys():
                print(obj)
                continue

            try:
                summarization = summarizer(content, ratio=0.2, max_words=-1)
                print("==>", summarization)
            except:
                print("----->", obj["source_url"])
                summarization = brief
        except:
            summarization = obj['brief_content']
        if len(summarization) == 0:
            summarization = obj['brief_content']
        try:
            item['text_rank'] = text_rank.run(content, ratio=0.2, max_words=-1)
            print("==> textrank:", item['text_rank'])
        except:
            item['text_rank'] = item['brief_content']

        try:
            db.news_tbl.update_one({"_id": id}, {"$set": {"summary": summarization}})
        except Exception as ex:
            print(obj["source_url"])
    except:
        pass
    
    try:
        doc_to_classify = obj['title'] + "\n" + obj['brief_content']
        label = classifier_daily.predict(sample=doc_to_classify)
        id = obj['_id']
        db.news_tbl.update_one({"_id": id}, {"$set": {"category": label['class'], "score": str(label['score'])}})
    except Exception as ex:
        print(obj["source_url"])


