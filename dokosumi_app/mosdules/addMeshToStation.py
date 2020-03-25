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


# class AddMeshToStation:
#     def __init__(self):
#         sample = ''

#     def addMeshToStation(self,keyword):

# 駅名のTSVリストを取得
station_tsv_file = 'D:\programs\Python\Dokosumi\data\station_list_kanto.tsv'
#station_tsv_file = 'D:\programs\Python\Dokosumi\data\station_list_test.tsv'
station_df = pd.read_table(station_tsv_file)

# メッシュのTSVリストを取得
mesh_tsv_file = 'D:\programs\Python\Dokosumi\data\mesh_kanto.tsv'
mesh_df = pd.read_table(mesh_tsv_file)

#駅名DataFrameに列を追加
station_df['MESH_CODES'] = ''
print(station_df)

# 駅名の数だけ検索
for row_s in station_df.itertuples():

    #検索対象の街を表示
    print(row_s.station_name)
    
    # メッシュの中心が駅から1.5km以内にある場合、駅名DataFrameにMESH_CODEを追加
    mesh_codes = []
    for row_m in mesh_df.itertuples():

        #メッシュの中心座標を取得
        lon_m = (row_m.lon_2B + row_m.lon_1A) / 2
        lat_m = (row_m.lat_2B + row_m.lat_1A) / 2

        #2点間の距離を取得
        dist = cal_rho(lon_m,lat_m,row_s.lon,row_s.lat)

        if dist < 1.5:
            mesh_codes.append(row_m.MESH_CODE)
            print('DISTANCE:' + str(dist))
            print('LAT:' + str(lat_m) + ' LON:' + str(lon_m))
            print('CORRECT:' + str(row_m.MESH_CODE))
    
    # 駅名DataFrameにMESH_CODESを追加
    station_df.at[row_s.Index, 'MESH_CODES'] = mesh_codes

print('DATAFLAME : ')
print(station_df)

#結果をTSVファイルに保存
dirname = os.path.dirname(station_tsv_file)
filename = os.path.basename(station_tsv_file)
station_df.to_csv(dirname + '\station_list_mesh.tsv', index=False, sep='\t')


