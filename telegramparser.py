import asyncio
import json
import configparser
import requests
from datetime import timedelta,datetime
from bs4 import BeautifulSoup
from natasha import NewsNERTagger, NewsEmbedding, Doc, Segmenter, NewsMorphTagger, NewsSyntaxParser
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import MessageEntityTextUrl

class TelegramParser():
    def __init__(self):
        self.economic_chats = ["forbesrussia", "economika"]
        self.datetime_format = "%Y-%m-%d %H:%M:%S"
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.api_id = int(self.config['Telegram']['api_id'])
        self.api_hash = self.config['Telegram']['api_hash']
        self.username = self.config['Telegram']['username']
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.client = TelegramClient(self.username, self.api_id, self.api_hash, loop=self.loop)
        self.client.start()
        self.segmenter = Segmenter()
        emb = NewsEmbedding()
        self.morph_tagger = NewsMorphTagger(emb)
        self.syntax_parser = NewsSyntaxParser(emb)
        self.ner_tagger = NewsNERTagger(emb)
        self.doc = Doc(" ")


    def get_organizations_from_news(self, last_message):
        self.doc.text=last_message.raw_text
        self.doc.segment(self.segmenter)
        self.doc.tag_morph(self.morph_tagger)
        self.doc.parse_syntax(self.syntax_parser)
        self.doc.tag_ner(self.ner_tagger)
        organizations = []
        for ner in self.doc.spans:
            if ner.type == 'ORG':
                organizations.append(ner.text)
        return organizations

    def get_news(self, id:int, date):
        all_news = []
        # здесь можно в timedelta задать hours=X или minutes=X
        current_utc_datetime = datetime.utcnow() - timedelta(days=1780)
        lithium_companies = {1: "Аэрофлот", 2: "Газпром", 3: "ВТБ",
                             4: "Сбер", 5: "Лукойл", 6: "Aplle"}
        limit = 100
        for chat in self.economic_chats:
            iterator = 0
            offset = 0
            flag = True
            while flag:
                last_messages = self.loop.run_until_complete(self.client(GetHistoryRequest(
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
                    # print(f"{chat} - {iterator}")
                    iterator += 1
                    dt = last_message.date.replace(tzinfo=None)
                    # print(dt.strftime(self.datetime_format))
                    if date > dt.strftime(self.datetime_format):
                        flag = False
                        break
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
                            organizations = list(set(self.get_organizations_from_news(last_message)))
                            for org in organizations:
                                if org in lithium_companies[id]:
                                    post = {'date_time': dt.strftime(self.datetime_format), 'title': title,
                                            'text': last_message.message,
                                            'source': chat, 'company_id': id,
                                            'url': f"https://t.me/{chat}/{last_message.id}"}
                                    all_news.append(post)
                                    break
                    else:
                        flag = False
                        break

        # with open('all_news_test.json', 'w', encoding='utf8') as outfile:
        #     json.dump(all_news, outfile, indent=2, ensure_ascii=False)
        return all_news


