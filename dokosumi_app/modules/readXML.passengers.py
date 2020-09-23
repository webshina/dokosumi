import sys
import googlemaps
import pprint # list型やdict型を見やすくprintするライブラリ
import keys
import requests
import json
import searchPointsByKeyword
import pandas as pd
import time
import os
import xml.etree.ElementTree as ET 
import glob

# 名前空間を取得
ns = {'gml': 'http://www.opengis.net/gml/3.2', 'ksj':'http://nlftp.mlit.go.jp/ksj/schemas/ksj-app', 'xlink':'http://www.w3.org/1999/xlink'}

# ファイル一覧を再帰的に取得
xml_list = glob.glob('D:\programs\Python\Dokosumi\data\駅別乗降客数\S12**\S12*.xml', recursive=True)
print(xml_list)

df_all = pd.DataFrame(columns=['STATION_NAME','SCORE'])

for xml_file in xml_list:

    print('XML_FILE:' + xml_file)

    # XMLファイルを解析
    tree = ET.parse(xml_file) 

    # XMLを取得
    root = tree.getroot()
    
    # # ksj:LandPrice以下を取得
    pointNodes = root.findall('ksj:TheNumberofTheStationPassengersGettingonandoff', ns)

    # SCORE DataFrameを作成
    df_score = pd.DataFrame(columns=['STATION_NAME','SCORE'])

    # DataFrameにid,SCOREを追加
    for itemNode in pointNodes:

        station_name = itemNode.find('ksj:stationName', ns).text.strip()
        print('station_name' + station_name)

        score = itemNode.find('ksj:passengers2015', ns).text.strip()
        print('score' + score)

        # DataFrameにid,座標を追加
        df_score_se = pd.Series([station_name, score], index=df_score.columns)
        print(df_score_se)
        df_score = df_score.append(df_score_se, ignore_index=True)

    df = df_score
    df_all = pd.concat([df_all, df], axis=0, join='inner')

# 同じ駅名の乗降客数を合計
df_all = df_all.groupby('STATION_NAME', as_index=False).sum()

print(df_all)
#結果をTSVファイルに保存
df_all.to_csv('D:\programs\Python\Dokosumi\data\score_by_latlon.tsv', index=False, sep='\t')