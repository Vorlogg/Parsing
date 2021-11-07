import requests
from bs4 import BeautifulSoup
import json

company_id_list = {1: ["Аэрофлот", "AFLT"], 2: ["Газпром", "Газпром"], 3: ["ВТБ", "ВТБ"], 4: ["Сбер", "Sber"],
                   5: ["Лукойл", "LKOH"], 6: ["Aplle", "AAPL"]}

for i in company_id_list.items():
    print(i[1][0])
    with open("{0}_smart-lab.json".format(i[1][0]), "r") as read_file:
        data = json.load(read_file)

    for j in data:
        print(j)


