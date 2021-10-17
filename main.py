import requests
from bs4 import BeautifulSoup


d=[]
for j in range(1):
    url = 'https://lenta.ru/tags/organizations/sberbank-rossii/1/'
    r = requests.get(url)
    NewsUrls=[]
    soup = BeautifulSoup(r.text, 'html.parser')
    for tag in soup.find_all("a"):
        print("{0}: {1}".format(tag.get('href'), tag.text))
        # if tag.get('href')==r"/news\S":
        if str(tag.get('href')).startswith("/news"):
            NewsUrls.append("https://lenta.ru"+tag.get('href'))


    print(NewsUrls)
for urls in NewsUrls[0:2]:
    news=requests.get(urls)
    soupnews = BeautifulSoup(news.text, 'html.parser')
    for text in soupnews.find_all("p"):
        print(text)





    # с помощью циклам перебераем товары на странице и получаем из них нужные параметры
    # for i in range(20):
    #     # получаем название товара
    #     product = soup.find_all('h3')[i].get_text()
    #     # получаем цену товара
    #     price = soup.find_all(class_='price_g')[i].get_text()
    #     # удаляем пробел из цены
    #     price = price.replace(" ", "")
    #     # получаем ссылку на товар
    #     link = soup.find_all(class_='show-popover ec-price-item-link', attrs={'data-role': 'product-cart-link'})[i][
    #         'href']
    #     # добавляем домен к ссылке
    #     link = 'www.dns-shop.ru' + link
    #     # добавляем данные о товаре в список
    #     d.append([product, price, link])

# # открываем файл на запись
# with open('sbp.csv', 'w') as ouf:
#     # перебираем элементы списка d
#     for i in d:
#         # преобразуем элемент списка в строку
#         i = str(i)
#         # очищаем строку от ненужных символов
#         i = i.replace("\'", "")
#         i = i.replace("[", "")
#         i = i.replace("]", "")
#         # записываем строку в файл
#         ouf.write(i + '\n')