import requests
from bs4 import BeautifulSoup
import webbrowser
from urllib.parse import urljoin
import lxml.html
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import os
import re
import pandas as pd
import urllib.parse

# 駅名のTSVファイルを取得
dirname = os.path.dirname(__file__)
tsv_file = dirname + '/../data/score_by_station.tsv'
station_name_df = pd.read_table(tsv_file)

#DataFrameに列を追加
station_name_df = pd.DataFrame(station_name_df['station_name'])
print(station_name_df)

#各駅から各駅への時間を再帰的に取得
for station_name_1 in station_name_df['station_name']:

    #駅Aから各駅までの所要時間を格納するDataFrameを取得
    TimeToArriveByStation_df = station_name_df

    #駅Aから各駅までの所要時間を取得
    for station_name_2 in station_name_df['station_name']:
        print(station_name_1 + ' to ' + station_name_2)

        #駅名が同じだった場合はスキップ
        if station_name_1 == station_name_2:
            #駅Aの駅Bまでの所要時間を更新
            TimeToArriveByStation_df[station_name_2] = 'None'
            continue

        station_name_1_encode = urllib.parse.quote(station_name_1)
        station_name_2_encode = urllib.parse.quote(station_name_2)

        #出発時刻を設定
        y = '2020'
        m = '11'
        d = '13'
        hh = '8'
        m2 = '0'
        m1 = '0'

        try:
            #駅から駅までの乗り換え情報取得
            get_url_info = requests.get('https://transit.yahoo.co.jp/search/result?from=' + station_name_1_encode + '&to=' + station_name_2_encode + '&y=' + y + '&m=' + m + '&d=' + d + '&hh=' + hh + '&m2=' + m2 + '&m1=' + m1)

            #ページソースを取得
            soup = BeautifulSoup(get_url_info.text, 'lxml')

            #時間取得
            time = soup.find("div", attrs={"id":"route01"})
            time = time.find("li", attrs={"class":"time"})
            time = time.get_text()
            #着～分で囲まれた文字列（時間）を取得
            time = re.search("(?<=\（乗車).+?(?=\）)", time).group()
            print('所要時間：'+time)

        #スクレイピング中にエラーが発生したら所要時間にErrorを設定
        except:
            time = 'Error'

        #駅Aの駅Bまでの所要時間を更新
        TimeToArriveByStation_df[station_name_2] = time
    
    #駅Aから各駅までの所要時間を格納
    TimeToStationAtoOtherStation_df = TimeToArriveByStation_df[TimeToArriveByStation_df.station_name == station_name_1]

    #CSVに出力
    #プログラムの実行ディレクトリを取得
    dirname = os.path.dirname(os.path.abspath(__file__))
    csv_file = dirname + '/TimeToArriveByStation.csv'
    if os.stat(csv_file).st_size == 0:
        TimeToStationAtoOtherStation_df.to_csv(csv_file, index=False, encoding="utf-8", mode='a', header=True)
    else:
        TimeToStationAtoOtherStation_df.to_csv(csv_file, index=False, encoding="utf-8", mode='a', header=False)
