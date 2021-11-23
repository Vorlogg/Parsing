import asyncio
import json
import configparser
import datetime
import requests
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
        self.asyncio.set_event_loop(self.loop)
        self.client = TelegramClient(self.username, self.api_id, self.api_hash, loop=self.loop)
        self.client.start()

    def get_organizations_from_news(self,last_message):
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


    def get_news(self):
        all_news = []
        # здесь можно в timedelta задать hours=X или minutes=X
        current_utc_datetime = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        # lithium_companies = get_all_companies_from_db()
        lithium_companies = [{"id": 1, "text": "Аэрофлот"}, {"id": 2, "text": "Газпром"}, {"id": 3, "text": "ВТБ"},
                             {"id": 4, "text": "Сбер"},
                             {"id": 5, "text": "Лукойл"}, {"id": 6, "text": "Aplle"}]
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
                            organizations = list(set(self.get_organizations_from_news(last_message)))
                            # print(organizations)
                            for org in organizations:
                                for lithium_company in lithium_companies:

                                    if org in lithium_company['text']:
                                        post = {'date_time': dt.strftime(self.datetime_format), 'title': title,
                                                'text': last_message.message,
                                                'source': chat, 'company_id': lithium_company['id'],
                                                'url': f"https://t.me/{chat}/{last_message.id}"}
                                        all_news.append(post)
                                        break
                    else:
                        flag = False
                        break

        # print(all_news)
        # with open('all_news_test.json', 'w', encoding='utf8') as outfile:
        #     json.dump(all_news, outfile, indent=2, ensure_ascii=False)
        return all_news




tg=TelegramParser()
date=tg.get_news()
print(date)