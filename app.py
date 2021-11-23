import asyncio
import json

from flask import Flask, jsonify
import configparser
import datetime
import requests
from bs4 import BeautifulSoup
import mysql.connector
from natasha import NewsNERTagger, NewsEmbedding, Doc, Segmenter, NewsMorphTagger, NewsSyntaxParser
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import MessageEntityTextUrl
from tqdm import tqdm
economic_chats = ["forbesrussia", "economika"]


# Не используется
def authorize():
    config = configparser.ConfigParser()
    config.read("config.ini")
    api_id = int(config['Telegram']['api_id'])
    api_hash = config['Telegram']['api_hash']
    username = config['Telegram']['username']
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client = TelegramClient(username, api_id, api_hash, loop=loop)
    client.start()
    return client


def get_all_companies_from_db():
    config = configparser.ConfigParser()
    config.read("config.ini")
    lithium_mysql_db = mysql.connector.connect(
        host=config['MySQL']['host'],
        port=int(config['MySQL']['port']),
        user=config['MySQL']['user'],
        password=config['MySQL']['password'],
        database=config['MySQL']['database'],
        charset=config['MySQL']['charset'],
        use_unicode=True
    )
    my_cursor = lithium_mysql_db.cursor()
    my_cursor.execute("SELECT id, name, ticker, description FROM companies")
    lithium_companies_ = my_cursor.fetchall()
    lithium_companies = []
    for lithium_company in lithium_companies_:
        text = ''
        comp_id = -1
        for item in lithium_company:
            text = text + ' ' + str(item)
            if type(item) is int:
                comp_id = item
        lithium_companies.append({'id': comp_id, 'text': text})
    return lithium_companies


def get_organizations_from_news(last_message):
    segmenter = Segmenter()
    emb = NewsEmbedding()
    morph_tagger = NewsMorphTagger(emb)
    syntax_parser = NewsSyntaxParser(emb)
    ner_tagger = NewsNERTagger(emb)
    doc = Doc(last_message.raw_text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    doc.parse_syntax(syntax_parser)
    doc.tag_ner(ner_tagger)
    organizations = []
    for ner in doc.spans:
        if ner.type == 'ORG':
            organizations.append(ner.text)
    return organizations


def get_news():
    all_news = []
    # здесь можно в timedelta задать hours=X или minutes=X
    current_utc_datetime = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    # lithium_companies = get_all_companies_from_db()
    lithium_companies = [{"id": 1, "text": "Аэрофлот"}, {"id": 2, "text": "Газпром"}, {"id": 3, "text": "ВТБ"},
                         {"id": 4, "text": "Сбер"},
                         {"id": 5, "text": "Лукойл"}, {"id": 6, "text": "Aplle"}]
    limit = 100
    for chat in economic_chats:
        iterator = 0
        offset = 0
        flag = True
        while flag:
            last_messages = loop.run_until_complete(client(GetHistoryRequest(
                peer=chat,
                limit=limit,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=offset,
                hash=0
            )))
            last_messages = last_messages.messages
            offset += limit
            for last_message in last_messages:
                print(f"{chat} - {iterator}")
                iterator += 1
                dt = last_message.date.replace(tzinfo=None)
                if dt >= current_utc_datetime:
                    title = ''
                    if last_message.entities is not None:
                        for entity in last_message.entities:
                            if type(entity) is MessageEntityTextUrl:
                                if entity.url is not None:
                                    try:
                                        url = entity.url
                                        reqs = requests.get(url)
                                        soup = BeautifulSoup(reqs.text, 'html.parser')
                                        title = soup.find_all('title')[0].get_text()
                                    except Exception:
                                        title = ''
                    if last_message.raw_text is not None:
                        organizations = list(set(get_organizations_from_news(last_message)))
                        # print(organizations)
                        for org in organizations:
                            for lithium_company in lithium_companies:

                                if org in lithium_company['text']:
                                    post = {'date_time': dt.strftime(datetime_format), 'title': title,
                                            'text': last_message.message,
                                            'source': chat, 'company_id': lithium_company['id'],
                                            'url': f"https://t.me/{chat}/{last_message.id}"}
                                    all_news.append(post)
                                    break
                else:
                    flag = False
                    break
    print(all_news)
    with open('all_news_test.json', 'w', encoding='utf8') as outfile:
        json.dump(all_news, outfile, indent=2, ensure_ascii=False)
    return all_news


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
datetime_format = "%Y-%m-%d %H:%M:%S"
config = configparser.ConfigParser()
config.read("config.ini")
api_id = int(config['Telegram']['api_id'])
api_hash = config['Telegram']['api_hash']
username = config['Telegram']['username']
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
client = TelegramClient(username, api_id, api_hash, loop=loop)
client.start()
# print(get_news())
@app.route('/')
def hello_world():
    # print(get_news())
    return 'Hello World!'


@app.route('/get_last_day_news')
def get_last_day_news():
    posts = get_news()
    return jsonify(posts)


if __name__ == '__main__':
    app.run()
