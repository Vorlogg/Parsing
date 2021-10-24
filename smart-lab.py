import requests
from bs4 import BeautifulSoup
import re
import json
from tqdm import tqdm
import pymorphy2

months = {"январь": "01", "февраль": "02", "март": "03", "апрель": "04", "май": "05", "июнь": "06", "июль": "07",
          "август": "08", "сентябрь": "09", "октябрь": "10", "ноябрь": "11", "декабрь": "12"}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
    "Accept-Encoding": "*",
    "Connection": "keep-alive"
}

morph = pymorphy2.MorphAnalyzer()

jsonDate = []
NewsUrls = []
company_id = 5
company_id_list = {1: ["Аэрофлот","AFLT"], 2: ["Газпром", "Газпром"], 3: ["ВТБ","ВТБ"], 4: ["Сбер","Sber"], 5: ["Лукойл","LKOH"], 6: ["Aplle","AAPL"]}
for j in tqdm(range(1, 28)):
    # print(j)
    url = "https://smart-lab.ru/forum/news/{0}/page{1}/".format(company_id_list[company_id][1], str(j))
    r = requests.get(url, timeout=10, headers=headers)
    if r.status_code == 200:
        # print(url)
        soup = BeautifulSoup(r.text, 'html.parser').find("div", class_="temp_block")
        # print(soup.find_all("a"))
        for tag in soup.find_all("a"):
            # print(tag.get("href"))
            strurls = tag.get("href")
            strurls = re.sub("/blog/", "", tag.get("href"))
            NewsUrls.append("https://smart-lab.ru/blog/news/" + strurls)

# print(NewsUrls)


for urls in tqdm(NewsUrls):
    try:
        textnews = ""
        news = requests.get(urls, timeout=10, headers=headers)
        # news.encoding = 'cp1251'
        if news.status_code == 200:
            soupnews = BeautifulSoup(news.text, 'html.parser')
            title = soupnews.find("h1").span.text
            date = soupnews.find(class_="date").text
            datespl = date.split()
            # print(datespl)
            year = datespl[2]
            day = datespl[0]
            year = re.sub(",", "", year)
            time = re.sub(",", "", datespl[3])
            time = time.split(':')
            moth = morph.parse(datespl[1])[0].normal_form
            dateend = "{0}-{1}-{2} {3}:{4}:{5}".format(year, months[moth], day, time[0], time[1], "00")
            # print(dateend)
            # print(title)

            textnews = soupnews.find_all("div", class_="content")[1].text

            # textnews = re.sub("^\n|\r", '', textnews)
            # textnews = re.sub(
            #     "INTERFAX.RU - ", '',
            #     textnews)
            # print(textnews)
            jsonDate.append(
                {"date_time": dateend, "title": title, "text": textnews,
                 "sourse": "{0} smart-lab".format(company_id_list[company_id][0]),
                 "company_id": company_id,
                 })

    except:
        print("err")

# print(len(jsonDate))
with open('{0}_smart-lab.json'.format(company_id_list[company_id][0]), 'w', encoding='utf-8') as file:
    json.dump(jsonDate, file, ensure_ascii=False, indent=2)
