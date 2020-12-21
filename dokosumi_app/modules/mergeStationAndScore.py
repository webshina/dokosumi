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
import math
import numpy as np
from sklearn import preprocessing

score_keywords = ['landPrice', 'access', 'population', 'park', 'flood', 'security', 'supermarket', 'livable']

# 駅名のTSVリストを取得
station_tsv_file = 'D:\programs\Python\Dokosumi\data\station_list_mesh_minamikanto.tsv'
station_df = pd.read_table(station_tsv_file, dtype=str)
station_df = station_df[['station_name']]
print(station_df)

#街の属性情報をマージ
station_attr_tsv_file = 'D:\programs\Python\Dokosumi\data\station_attributes.tsv'
station_attr_df = pd.read_table(station_attr_tsv_file, dtype=str)
station_attr_df = station_attr_df[['station_name', 'lon', 'lat', 'comment', 'pref', 'suumoEkiCode', 'access_remark', 'landPrice_remark', 'security_remark', 'supermarket_remark']]
station_df = pd.merge(station_df, station_attr_df, on='station_name', how='inner')
print(station_df)

#街の統計情報をマージ
base_df = station_df
for score_keyword in score_keywords:

    # 緯度経度ごとのSCOREのTSVリストを取得
    score_tsv_file = 'D:\programs\Python\Dokosumi\data\score_by_station\\' + score_keyword + '_by_station.tsv'
    score_df = pd.read_table(score_tsv_file)

    # 駅名のTSVリストにある駅のみ抽出
    score_df = pd.merge(base_df, score_df, on='station_name', how='inner')
    print(score_df)
    score_df = score_df[['station_name', 'SCORE']]
    print(score_df)

    ## 効用関数を適用
    # score_np = np.log(score_df['SCORE'].values + 1)
    score_np = score_df['SCORE'].values
    # 最大1最小0で正規化
    score_np = (score_np - score_np.min()).astype(float) / (score_np.max() - score_np.min()).astype(float)

    score_df['SCORE'] = score_np * 100


    # 列名の変更
    score_df = score_df.rename(columns={'SCORE' : score_keyword})

    # 駅名DataFrameとScore DataFrameをマージ
    base_df = pd.merge(base_df, score_df, on='station_name')
    print(base_df)

#結果をTSVファイルに保存
dirname = os.path.dirname(station_tsv_file)
filename = os.path.basename(station_tsv_file)
base_df.to_csv('D:\programs\Python\Dokosumi\dokosumi_app\data\score_by_station.tsv', index=False, sep='\t')
