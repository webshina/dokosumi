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

#マージ対象のJSONファイルを取得
json_files = glob.glob('D:\programs\Python\Dokosumi\data\元データ\駅から駅への経路情報\\routes_stationA_to_stationB*.json')

#各駅から各駅への経路情報を格納する辞書を作成
routes_stationA_to_stationB = {}

for json_file in json_files:
    print("マージ開始：" + json_file)
    
    #ファイルが存在する場合は取得
    with open(json_file, mode="r", encoding="utf-8") as f:
        routes_stationA_to_stationB.update(json.load(f))

#保存先を取得
json_file = 'D:\programs\Python\Dokosumi\data\元データ\駅から駅への経路情報\\routes_stationA_to_stationB.json'
#JSONに出力
with open(json_file, mode="w", encoding="utf-8") as f:
    json.dump(routes_stationA_to_stationB, f, indent=4, ensure_ascii=False)


# 駅名のTSVファイルを取得
dirname = os.path.dirname(__file__)
tsv_file = 'D:\programs\Python\Dokosumi\dokosumi_app\data\score_by_station.tsv'
station_list_df = pd.read_table(tsv_file)
station_list_all = station_list_df["station_name"].values.tolist()


#各駅から各駅への時間を再帰的に取得
for station_name_2 in station_list_all:

    #駅Aから各駅までの所要時間を取得
    routes_stationA_to_stationB_divide_by_station = {}
    for station_name_1 in station_list_all:
        print(station_name_1 + ' to ' + station_name_2)

        if routes_stationA_to_stationB.get(station_name_1 + '_' + station_name_2,'') != '':
            routes_stationA_to_stationB_divide_by_station[station_name_1 + '_' + station_name_2] = routes_stationA_to_stationB.get(station_name_1 + '_' + station_name_2,'')
            
    #保存先を取得
    json_file = 'D:\programs\Python\Dokosumi\dokosumi_app\data\\routes_stationA_to_stationB\\to_' + station_name_2 + '.json'
    #JSONに出力
    with open(json_file, mode="w", encoding="utf-8") as f:
        json.dump(routes_stationA_to_stationB_divide_by_station, f, indent=4, ensure_ascii=False)