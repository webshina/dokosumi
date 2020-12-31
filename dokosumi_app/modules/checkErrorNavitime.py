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
import pickle
import json
import glob


# 各駅から各駅への経路情報のJSONファイルを取得
json_file = 'D:\programs\Python\Dokosumi\data\元データ\駅から駅への経路情報\\routes_stationA_to_stationB.json'
with open(json_file) as f:
    routes_stationA_to_stationB = json.load(f)

# 駅名のTSVファイルを取得
dirname = os.path.dirname(__file__)
tsv_file = 'D:\programs\Python\Dokosumi\dokosumi_app\data\score_by_station.tsv'
stationA_to_stationB_df = pd.DataFrame(pd.read_table(tsv_file)["station_name"])
#リスト化
stationA_to_stationB_list = stationA_to_stationB_df["station_name"].values.tolist()

#駅Aから各駅までの混雑度を格納するDataFrameを取得
for station_name in stationA_to_stationB_list:
    stationA_to_stationB_df[station_name] = 0

#各駅から各駅への時間を再帰的に取得
for station_name_1 in stationA_to_stationB_list:

    for station_name_2 in stationA_to_stationB_list:
        print(station_name_1 + ' to ' + station_name_2)

        if station_name_1 == station_name_2:
            continue

        route_stationA_to_stationB = routes_stationA_to_stationB.get(station_name_1 + '_' + station_name_2,'')
        if route_stationA_to_stationB != "":
            #時間の合計値を格納するリストを作成
            times = []
            for key in route_stationA_to_stationB.keys():
                block = route_stationA_to_stationB[key]
                if block.get("route_block", 0) == 1:
                    time = block.get("time")

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

                    times.append(time)

            if sum(times) > 240:
                stationA_to_stationB_df.loc[stationA_to_stationB_df["station_name"] == station_name_1, station_name_2] = "TIME_NG"
        else:
            stationA_to_stationB_df.loc[stationA_to_stationB_df["station_name"] == station_name_1, station_name_2] = "KEY_NG"

#結果をTSVファイルに保存
stationA_to_stationB_df.to_csv("D:\programs\Python\Dokosumi\data\元データ\駅から駅への経路情報\error_stations.tsv", index=False, sep='\t')