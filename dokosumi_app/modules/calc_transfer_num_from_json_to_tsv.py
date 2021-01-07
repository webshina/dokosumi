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
import json

# 駅名のTSVファイルを取得
tsv_file = 'D:\programs\Python\Dokosumi\dokosumi_app\data\score_by_station.tsv'
score_by_station_df = pd.read_table(tsv_file)

#駅名だけ抽出
station_name_df = pd.DataFrame(score_by_station_df['station_name'])

# 各駅から各駅への経路情報のJSONファイルを取得
json_file = 'D:\programs\Python\Dokosumi\data\元データ\駅から駅への経路情報\\routes_stationA_to_stationB.json'
with open(json_file, mode="r", encoding="utf-8") as f:
    routes_dict = json.load(f)

#駅Aから各駅までの乗り換え回数を格納するDataFrameを取得
transfer_num_df = station_name_df
for station_name in station_name_df['station_name']:
    # 乗り換え回数が取得できない場合はとりあえずデフォルト値をセット
    transfer_num_df[station_name] = 3

#各駅から各駅への時間を再帰的に取得
for station_name_1 in station_name_df['station_name']:

    # 各駅の混雑度を計算
    for station_name_2 in station_name_df["station_name"]:
        print("各駅から職場の最寄り駅への経路取得：" + station_name_1 + "から" + station_name_2)

        if station_name_1 != station_name_2:
            
            #各駅から職場の最寄り駅への経路情報取得
            route_dict = routes_dict.get(station_name_1 + '_' + station_name_2, '')

            if route_dict != '':
                #経路情報から乗り換え回数を取得
                time_transfer_num = route_dict.get("numberOfTransfer","").replace("回","")
                
                if time_transfer_num != '':
                    # DataFrameのアップデート
                    transfer_num_df[station_name_2].loc[transfer_num_df['station_name'] == station_name_1] = time_transfer_num
                else:
                    # 乗り換え回数が取得できない場合はとりあえずデフォルト値をセット
                    time_transfer_num = 3
            else:
                print("Not Found")
                continue
        else:
            transfer_num_df[station_name_2].loc[transfer_num_df['station_name'] == station_name_1] = 0

#結果をTSVファイルに保存
transfer_num_df.to_csv("D:\programs\Python\Dokosumi\dokosumi_app\data\\transfer_num_stationA_to_stationB.tsv", index=False, sep='\t')