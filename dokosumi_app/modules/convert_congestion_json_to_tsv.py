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
with open(json_file) as f:
    routes_dict = json.load(f)

#駅Aから各駅までの混雑度を格納するDataFrameを取得
congestions_df = station_name_df
for station_name in station_name_df['station_name']:
    congestions_df[station_name] = 50.0

#各駅から各駅への時間を再帰的に取得
for station_name_1 in station_name_df['station_name']:

    # 各駅の混雑度を計算
    for station_name_2 in station_name_df["station_name"]:
        print("各駅から職場の最寄り駅への経路取得：" + station_name_1 + "から" + station_name_2)

        if station_name_1 != station_name_2:
            
            #各駅から職場の最寄り駅への経路情報取得
            route_dict = routes_dict.get(station_name_1 + '_' + station_name_2, '')

            if route_dict != '':
                #経路情報から合計乗車時間・乗車時間*混雑度を取得
                times = []
                time_congestions = []
                for value in route_dict.values():
                    if value.get("route_block","") == 1:
                        #時間のフォーマット変換 分単位に直す
                        time = value.get('time', 0)
                        
                        #時間を取得
                        hh = re.match(r'(.*?)時間.*', time)
                        if hh != None:
                            hh = float(hh.group(1))
                        else:
                            hh = 0.0
                        
                        #分を取得
                        mm = re.match(r'.*時間(.*?)分.*', time)
                        if mm != None:
                            mm = float(mm.group(1))
                        else:
                            mm = re.match(r'(.*?)分.*', time)
                            if mm != None:
                                mm = float(mm.group(1))
                            else:
                                mm = 0.0
                        
                        #分単位に換算
                        time = hh * 60 + mm

                        #混雑度を数値に変換
                        congestion = value.get("congestion","")
                        if congestion == "余裕で座れる":
                            congestion_score = 1.0
                        elif congestion == "席はいっぱい":
                            congestion_score = 0.3
                        elif congestion == "普通に立てる":
                            congestion_score = 0.5
                        elif congestion == "圧迫される":
                            congestion_score = 0.7
                        elif congestion == "身動き不可":
                            congestion_score = 0.8
                        elif congestion == "乗れない":
                            congestion_score = 0.0
                        else:
                            congestion_score = 0.5

                        #合計乗車時間・乗車時間*混雑度を取得
                        times.append(time)
                        time_congestions.append(time * congestion_score)

                    else:
                        continue
                
                #平均混雑度を取得
                if sum(times) != 0:
                    congestion_avg = sum(time_congestions) / sum(times)
                else:
                    congestion_avg = 1
                
                # DataFrameのアップデート
                congestions_df[station_name_2].loc[congestions_df['station_name'] == station_name_1] = congestion_avg * 100
            else:
                print("Not Found")
                continue
        else:
            congestions_df[station_name_2].loc[congestions_df['station_name'] == station_name_1] = 100

#結果をTSVファイルに保存
congestions_df.to_csv("D:\programs\Python\Dokosumi\dokosumi_app\data\congestion_stationA_to_stationB.tsv", index=False, sep='\t')