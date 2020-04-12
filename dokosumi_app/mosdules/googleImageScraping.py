import requests
import random
import shutil
import bs4
import ssl
import os
import pandas as pd

ssl._create_default_https_context = ssl._create_unverified_context

def image(data):
    Res = requests.get("https://www.google.com/search?hl=jp&q=" + data + "&btnG=Google+Search&tbs=0&safe=off&tbm=isch")
    Html = Res.text
    Soup = bs4.BeautifulSoup(Html,'lxml')
    links = Soup.find_all("img")
    for i in links:
        link = i.get("src")
        if link is not None and link.find('http') == 0:
            break
    return link

def download_img(url, file_name):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open('dokosumi_app/data/town_img/' + file_name + ".png", 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)


# 駅名のTSVファイルを取得
dirname = os.path.dirname(__file__)
score_df = pd.read_table('dokosumi_app/data/score_by_station.tsv')

stations = score_df['station_name']

for station in stations:
    data = station + ' 町並み'
    link = image(data)
    download_img(link, station)
    print("OK")