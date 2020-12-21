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

# 駅名のTSVファイルを取得
dirname = os.path.dirname(__file__)
tsv_file = 'D:\programs\Python\Dokosumi\dokosumi_app\data\score_by_station.tsv'
station_list_df = pd.read_table(tsv_file)
station_list_all = station_list_df["station_name"].values.tolist()
#対象を限定
station_list = station_list_all[int(sys.argv[1]):int(sys.argv[2])]
print(station_list)

#保存先を取得
json_file = 'D:\programs\Python\Dokosumi\dokosumi_app\data\\routes_stationA_to_stationB.json'

#ファイルが存在する場合は取得
if os.path.exists(json_file):
    with open(json_file) as f:
        routes_stationA_to_stationB_existing = json.load(f)
else:
    routes_stationA_to_stationB_existing = {}

#各駅から各駅への経路情報を格納する辞書を作成
routes_stationA_to_stationB = {}

#各駅から各駅への時間を再帰的に取得
for station_name_1 in station_list:

    #駅Aから各駅までの所要時間を取得
    for station_name_2 in station_list_all:
        print(station_name_1 + ' to ' + station_name_2)

        #jsonファイルに対象の駅が存在しない場合は処理開始
        if routes_stationA_to_stationB_existing.get(str(station_name_1) + "_" + str(station_name_2), "") == "" and station_name_1 != station_name_2:

            route_items = {}

            #経路リストに発車駅を格納
            route_items["start_station_name"] = station_name_1
            #経路リストに到着駅を格納
            route_items["goal_station_name"] = station_name_2

            station_name_1_encode = urllib.parse.quote(station_name_1)
            station_name_2_encode = urllib.parse.quote(station_name_2)

            #出発時刻を設定
            y = '2020'
            m = '12'
            d = '21'
            hh = '8'
            m2 = '0'
            m1 = '0'

            try:
                #駅から駅までの乗り換え情報取得
                url = 'https://www.navitime.co.jp/transfer/searchlist?orvStationName=' + station_name_1_encode + '&dnvStationName=' + station_name_2_encode + \
                    '&year=' + y + '&month=' + m + '&day=' + d + '&hour=' + hh + '&minute=' + m1 + \
                    '&basis=1&freePass=0&sort=0&wspeed=100&airplane=0&sprexprs=0&utrexprs=1&othexprs=1&mtrplbus=1&intercitybus=1&ferry=0'
                print(url)
                get_url_info = requests.get(url)

                #ページソースを取得
                soup = BeautifulSoup(get_url_info.text, 'lxml')
                
                #所要時間・運賃・乗り換え回数の取得
                item = soup.find("div", attrs={"class":"section_header_frame time"})

                #所要時間の取得
                time = item.find("dd", attrs={"class":"left"}).get_text()
                route_items["time"] = time

                #運賃の取得
                #IC運賃が存在する場合
                if item.find("span", attrs={"id":"total-ic-fare-text1"}) != None:
                    fare = item.find("span", attrs={"id":"total-ic-fare-text1"}).get_text()
                #IC運賃が存在しない場合
                else :
                    fare = item.find("span", attrs={"id":"total-fare-text1"}).get_text()


                route_items["fare"] = fare
                #乗り換え回数   
                numberOfTransfer = item.find("dl", attrs={"class":"left section_header_transfer_frame"})
                numberOfTransfer = numberOfTransfer.find("dd").get_text()
                route_items["numberOfTransfer"] = numberOfTransfer

                #時間取得
                #1つ目のルートを取得
                route = soup.find("div", attrs={"class":"section_detail_frame"})

                #駅名ブロック or 経路ブロックを取得
                route = route.find_all("div", attrs={"class":["section_station_frame","detail_frame"]})

                num = 0
                #各種経路情報を格納する辞書を作成
                route_items = {}
                for item in route:

                    #ひとつの経路情報を格納する辞書を作成
                    route_item = {}
                    
                    #駅名ブロックの場合
                    if item.attrs["class"][0] == "section_station_frame":
                        route_item["station_block"] = 1
                        #駅名取得
                        station_name = item.find("dt", attrs={"class":"left"})
                        station_name = station_name.find("a").get_text()
                        route_item["station_name"] = station_name
                        
                    #経路ブロックの場合
                    if item.attrs["class"][0] == "detail_frame":
                        route_item["route_block"] = 1

                        #所要時間取得
                        time = item.find("ul", attrs={"class":"time_info"}).find("li").get_text().replace("\n","").replace("\t","")
                        route_item["time"] = time
                        
                        #路線名・混雑度取得
                        line_congestion = item.find("div", attrs={"class":"railroad-area"})
                        #路線名取得
                        line = item.find("dt").get_text().replace("\xa0"," ")
                        route_item["line"] = line
                        
                        #混雑度取得
                        congestion = item.find("img", attrs={"class":"section-congestion-icon"})["src"]
                        #混雑度の画像名を取得
                        congestion = congestion.split("/")[-1]
                        #コメントに変換
                        if congestion == "congestion_1.png":
                            congestion = "余裕で座れる"
                        elif congestion == "congestion_2.png":
                            congestion = "席はいっぱい"
                        elif congestion == "congestion_3.png":
                            congestion = "普通に立てる"
                        elif congestion == "congestion_4.png":
                            congestion = "圧迫される"
                        elif congestion == "congestion_5.png":
                            congestion = "身動き不可"
                        elif congestion == "congestion_6.png":
                            congestion = "乗れない"
                        else:
                            congestion = "不明"

                        route_item["congestion"] = congestion
                    
                    #連番を作成
                    route_items[num] = route_item
                    num = num + 1

                routes_stationA_to_stationB[station_name_1 + "_" + station_name_2] = route_items

            #スクレイピング中にエラーが発生したら所要時間にErrorを設定
            except Exception as e:
                print(e)
        
        else:
            pass

#保存先を取得
json_file = 'D:\programs\Python\Dokosumi\dokosumi_app\data\\routes_stationA_to_stationB' + sys.argv[1] + "_" + sys.argv[2] + '.json'
#JSONに出力
with open(json_file, mode="w") as f:
    json.dump(routes_stationA_to_stationB, f, indent=4, ensure_ascii=False)