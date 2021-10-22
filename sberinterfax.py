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
for j in tqdm(range(28)):
    url = 'https://www.interfax.ru/tags/%D1%E1%E5%F0%E1%E0%ED%EA/page_' + str(j)
    r = requests.get(url, timeout=10, headers=headers)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser').find('div', class_='sPageResult')
        for tag in soup.find_all("h3"):
            NewsUrls.append("https://www.interfax.ru" + tag.a.get('href'))

# print(NewsUrls)
for urls in tqdm(NewsUrls):
    try:
        textnews = ""
        news = requests.get(urls, timeout=10, headers=headers)
        news.encoding = 'cp1251'
        if news.status_code == 200:
            soupnews = BeautifulSoup(news.text, 'html.parser').find('div', class_="infinitblock")
            title = soupnews.find("h1").text
            date = soupnews.find("a", class_="time").text
            datespl = date.split()
            year = datespl[3]
            day = datespl[1]
            time = re.sub(",", "", datespl[0])
            time = time.split(':')
            moth = morph.parse(datespl[2])[0].normal_form
            dateend = "{0}-{1}-{2} {3}:{4}:{5}".format(year, months[moth], day, time[0], time[1], "00")
            # print(dateend)
            # print(title)
            for text in soupnews.find_all("p"):
                textnews += text.text

            textnews = re.sub("^\n|\r", '', textnews)
            textnews = re.sub(
                "INTERFAX.RU - ", '',
                textnews)
            # print(textnews)
            jsonDate.append(
                {"date_time": dateend, "title": title, "text": textnews, "sourse": "Сбербанк interfax",
                 "company_id": None,
                 })

    except:
        print("err")


# # yyyy-MM-dd
print(len(jsonDate))
with open('Sber_interfax(2018-2021).json', 'w', encoding='utf-8') as file:
    json.dump(jsonDate, file, ensure_ascii=False,indent=2)
