import requests
from bs4 import BeautifulSoup
import re
import json
from tqdm import tqdm
import pymorphy2

months = {"январь": "01", "февраль": "02", "март": "03", "апрель": "04", "май": "05", "июнь": "06", "июль": "07",
         "август": "08", "сентябрь": "09", "октябрь": "10", "ноябрь": "11", "декабрь": "12"}

morph = pymorphy2.MorphAnalyzer()
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
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
    "Accept-Encoding": "*",
    "Connection": "keep-alive"
}
jsonDate = []
NewsUrls = []
for j in tqdm(range(402)):
    url = 'https://www.sberbank.ru/ru/press_center/all?page=' + str(j)
    r = requests.get(url, timeout=10, headers=headers)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        for tag in soup.find_all("a", class_="na-article"):
            # print("url: https://www.sberbank.ru{0} , text:{1}, date:{2}".format(tag.get('href'), tag.text, tag.span))
            NewsUrls.append("https://www.sberbank.ru" + tag.get('href'))

print(len(NewsUrls))
for urls in tqdm(NewsUrls):
    textnews = ""
    try:
        news = requests.get(urls, timeout=10, headers=headers)
        if news.status_code == 200:
            soupnews = BeautifulSoup(news.text, 'html.parser')
            title = soupnews.find("h1", class_="np-title").text
            date = soupnews.find("div", class_="np-date").text
            datespl=date.split()
            # print(datespl)
            moth = morph.parse(datespl[1])[0].normal_form
            year=datespl[0]
            day=datespl[2]
            dateend="{0}-{1}-{2} {3}:{4}:{5}".format(year,months[moth],day,"00","00","00")
            # print(dateend)
            # date1=
            # print(title)
            # print(soupnews.find("div",class_="np-body"))
            for text in soupnews.find_all("p"):
                textnews += text.text
            textnews += soupnews.find("div", class_="np-body").text
            # textnews=re.sub("^\n|\r", '', textnews)
            textnews = re.sub(
                "media@sberbank.ruРоссия, Москва, 117997, ул. Вавилова, 19© 1997—2021 ПАО Сбербанк.|" + title, '',
                textnews)
            # print(textnews)
            jsonDate.append(
                {"date_time": dateend, "title": title, "text": textnews, "sourse": "Сбербанк офф сайт", "company_id": None,
                 })
    except:
        print("error")
# yyyy-MM-dd
# print(jsonDate)
with open('Sber_off_site(2018-2021).json', 'w', encoding='utf-8') as file:
    json.dump(jsonDate, file, ensure_ascii=False,indent=2)
