import requests
from bs4 import BeautifulSoup
import re
import json
from tqdm import tqdm

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36 OPR/40.0.2308.81',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'DNT': '1',
    'Accept-Encoding': 'gzip, deflate, lzma, sdch',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4'
}
jsonDate = []
NewsUrls = []
for j in tqdm(range(402)):
    url = 'https://www.sberbank.ru/ru/press_center/all?page=' + str(j)
    r = requests.get(url, headers=headers)
    if r.status_code==200:
        soup = BeautifulSoup(r.text, 'html.parser')
        for tag in soup.find_all("a", class_="na-article"):
            # print("url: https://www.sberbank.ru{0} , text:{1}, date:{2}".format(tag.get('href'), tag.text, tag.span))
            NewsUrls.append("https://www.sberbank.ru" + tag.get('href'))

print(len(NewsUrls))
for urls in tqdm(NewsUrls):
    textnews = ""
    news = requests.get(urls, headers=headers)
    if r.status_code == 200:
        soupnews = BeautifulSoup(news.text, 'html.parser')
        try:
            title = soupnews.find("h1", class_="np-title").text
            date = soupnews.find("div", class_="np-date").text
            # print(date)
            # print(title)
            # print(soupnews.find("div",class_="np-body"))
            for text in soupnews.find_all("p"):
                textnews += text.text
            textnews += soupnews.find("div", class_="np-body").text
            # textnews=re.sub("^\n|\r", '', textnews)
            textnews = re.sub("media@sberbank.ruРоссия, Москва, 117997, ул. Вавилова, 19© 1997—2021 ПАО Сбербанк.|" + title, '',
                              textnews)
            # print(textnews)
            jsonDate.append(
            {"date_time": date, "title": title, "text": textnews, "sourse": "Сбербанк офф сайт", "company_id": None,
             "result_id": None})
        except:
            print("error")

# print(jsonDate)
with open('Sber_off_site(2018-2021).json', 'w', encoding='utf-8') as file:
    json.dump(jsonDate, file, ensure_ascii=False,indent=2)
