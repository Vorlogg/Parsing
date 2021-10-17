import requests
from bs4 import BeautifulSoup
import re

mystr = " balabla\n zzz "

re.sub("^\s+|\n|\r|\s+$", '', mystr)

headers ={
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36 OPR/40.0.2308.81',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'DNT': '1',
    'Accept-Encoding': 'gzip, deflate, lzma, sdch',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4'
}
d=[]
for j in range(1):
    url = 'https://www.sberbank.ru/ru/press_center/all?page=1'
    r = requests.get(url,headers=headers)
    NewsUrls=[]
    soup = BeautifulSoup(r.text, 'html.parser')
    for tag in soup.find_all("a", class_="na-article"):
        print("url: https://www.sberbank.ru{0} , text:{1}, date:{2}".format(tag.get('href'), tag.text, tag.span))
        NewsUrls.append("https://www.sberbank.ru"+tag.get('href'))

    print(NewsUrls)
for urls in NewsUrls:
    textnews=""
    news=requests.get(urls,headers=headers)
    soupnews = BeautifulSoup(news.text, 'html.parser')
    title=soupnews.find("h1",class_="np-title").text
    date=soupnews.find("div",class_="np-date").text
    print(date)
    print(title)
    # print(soupnews.find("div",class_="np-body"))
    for text in soupnews.find_all("p"):
        textnews+=text.text
    textnews+=soupnews.find("div",class_="np-body").text
    # textnews=re.sub("^\n|\r", '', textnews)
    textnews=re.sub("media@sberbank.ruРоссия, Москва, 117997, ул. Вавилова, 19© 1997—2021 ПАО Сбербанк.|"+title, '', textnews)
    print(textnews)
