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

score_keywords = ['landPrice', 'access', 'population', 'park', 'flood', 'security']

# 駅名のTSVリストを取得
station_tsv_file = 'D:\programs\Python\Dokosumi\data\station_list_mesh_kanto.tsv'
station_df = pd.read_table(station_tsv_file)
station_df = station_df[['station_name', 'lon', 'lat']]
#station_df.set_index("station_name")
print(station_df)

base_df = station_df
for score_keyword in score_keywords:

    # 緯度経度ごとのSCOREのTSVリストを取得
    score_tsv_file = 'D:\programs\Python\Dokosumi\data\score_by_station\\' + score_keyword + '_by_station.tsv'
    score_df = pd.read_table(score_tsv_file)
    score_df = score_df[['station_name', 'SCORE']]
    # 効用関数を適用
    score_np = np.log(score_df['SCORE'].values + 1)
    # 最大1最小0で正規化
    score_np = (score_np - score_np.min()).astype(float) / (score_np.max() - score_np.min()).astype(float)

    score_df['SCORE'] = score_np * 100

    # 列名の変更
    score_df = score_df.rename(columns={'SCORE' : score_keyword})

    # 駅名DataFrameとScore DataFrameをマージ
    base_df = pd.merge(base_df, score_df, on='station_name')

#結果をTSVファイルに保存
dirname = os.path.dirname(station_tsv_file)
filename = os.path.basename(station_tsv_file)
base_df.to_csv(dirname + '\score_by_station\score_by_station.tsv', index=False, sep='\t')
