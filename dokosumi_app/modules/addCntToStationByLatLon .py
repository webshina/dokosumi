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

#２点の緯度経度から距離を算出
def cal_rho(lon_a,lat_a,lon_b,lat_b):
    ra=6378.140  # equatorial radius (km)
    rb=6356.755  # polar radius (km)
    F=(ra-rb)/ra # flattening of the earth
    rad_lat_a=np.radians(lat_a)
    rad_lon_a=np.radians(lon_a)
    rad_lat_b=np.radians(lat_b)
    rad_lon_b=np.radians(lon_b)
    pa=np.arctan(rb/ra*np.tan(rad_lat_a))
    pb=np.arctan(rb/ra*np.tan(rad_lat_b))
    xx=np.arccos(np.sin(pa)*np.sin(pb)+np.cos(pa)*np.cos(pb)*np.cos(rad_lon_a-rad_lon_b))
    c1=(np.sin(xx)-xx)*(np.sin(pa)+np.sin(pb))**2/np.cos(xx/2)**2
    c2=(np.sin(xx)+xx)*(np.sin(pa)-np.sin(pb))**2/np.sin(xx/2)**2
    dr=F/8*(c1-c2)
    rho=ra*(xx+dr)
    return rho

# 駅名のTSVリストを取得
station_tsv_file = 'D:\programs\Python\Dokosumi\data\station_list_mesh_kanto.tsv'
station_df = pd.read_table(station_tsv_file)

# 緯度経度ごとのSCOREのTSVリストを取得
score_tsv_file = 'D:\programs\Python\Dokosumi\data\park_by_latlon.tsv'
score_df = pd.read_table(score_tsv_file)

#駅名DataFrameに列を追加
station_df['SCORE'] = ''

# 駅名の数だけ検索
for row_station in station_df.itertuples():

    #検索対象の街を表示
    print(row_station.station_name)
    
    # メッシュの中心が駅から1.5km以内にある場合、scoreを加算・平均値を取得
    score = 0
    cnt = 0
    for row_score in score_df.itertuples():

        #SCOREの中心座標を取得
        latlon = str(row_score.LATLON).split()
        lat_score =latlon[0]
        lon_score =latlon[1]

        #2点間の距離を取得
        dist = cal_rho(float(lon_score),float(lat_score),row_station.lon,row_station.lat)

        if dist < 1.5:
            # score += row_score.SCORE
            cnt += 1
            #print('DISTANCE:' + str(dist))
            #print('CORRECT:' + str(score))
    
    # SCOREの平均値を取得
    if cnt != 0:
        score = score / cnt
    elif cnt == 0:
        # ポイントがない場合は適当な価を設定
        score = 10000

    # 駅名DataFrameにscoreを追加
    score = cnt
    station_df.at[row_station.Index, 'SCORE'] = score
    print('SCORE:' + str(score))

station_df = station_df[['station_id', 'station_name', 'line_cd', 'pref_cd', 'post', 'add', 'lon', 'lat', 'SCORE']]
print('DATAFLAME : ')
print(station_df)

#結果をTSVファイルに保存
dirname = os.path.dirname(score_tsv_file)
filename = os.path.basename(score_tsv_file)
station_df.to_csv(dirname + '\score_by_station\\' + filename, index=False, sep='\t')

