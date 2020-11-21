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
import sys

# 駅名のTSVファイルを取得
dirname = os.path.dirname(__file__)
tsv_file = dirname + '/TimeToArriveByStation_Errors.tsv'
time_by_station_df = pd.read_table(tsv_file, index_col=0)
print(time_by_station_df.columns.values)

#各駅から各駅への時間を再帰的に取得
for station_name_1 in time_by_station_df.index.values:

    #駅Aから各駅までの所要時間を取得
    for station_name_2 in time_by_station_df.columns.values:
        print(station_name_1 + ' to ' + station_name_2)

        #時間がErrorだった場合は処理開始
        time = time_by_station_df.at[station_name_1, station_name_2]
        if time == 'Error':

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
                url = 'https://transit.yahoo.co.jp/search/result?from=' + station_name_1_encode + '&to=' + station_name_2_encode + '&y=' + y + '&m=' + m + '&d=' + d + '&hh=' + hh + '&m2=' + m2 + '&m1=' + m1 + '&flatlon=&fromgid=&type=1&ticket=ic&expkind=1&ws=3&s=0&al=1&shin=1&ex=1&hb=1&lb=1&sr=1&viacode=&via=&tlatlon=&togid='
                print(url)
                get_url_info = requests.get(url)

                #ページソースを取得
                soup = BeautifulSoup(get_url_info.text, 'lxml')

                #時間取得
                time = soup.find("div", attrs={"id":"route01"})
                time = time.find("li", attrs={"class":"time"})
                time = time.get_text()
                #着～分で囲まれた文字列（時間）を取得
                time = re.search("(?<=\（乗車).+?(?=\）)", time).group()

            #スクレイピング中にエラーが発生したら所要時間にErrorを設定
            except Exception as e:
                print(e)
                time = 'Error'
            
            print('所要時間：'+time)

            #駅Aの駅Bまでの所要時間を更新
            time_by_station_df.at[station_name_1,station_name_2] = time
        else:
            pass

#プログラムの実行ディレクトリを取得
dirname = os.path.dirname(os.path.abspath(__file__))
csv_file = dirname + '/TimeToArriveByStation_Modified_Errors.csv'

#CSVに出力
time_by_station_df.to_csv(csv_file, index=True, encoding="utf-8", mode='w', header=True)
