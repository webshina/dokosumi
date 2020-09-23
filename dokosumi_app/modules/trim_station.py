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

# 駅名のTSVリストを取得
station_tsv_file = 'D:\programs\Python\Dokosumi\data\station_list_mesh_kanto.tsv'
station_df = pd.read_table(station_tsv_file)
print(station_df)

# station_df = station_df[(station_df['pref_cd'] == '11') | (station_df['pref_cd'] == '12') | (station_df['pref_cd'] == '13') | (station_df['pref_cd'] == '14')]
station_df = station_df[(station_df["pref_cd"]==11) | (station_df["pref_cd"]==12) | (station_df["pref_cd"]==13) | (station_df["pref_cd"]==14)]
print(station_df)

#結果をTSVファイルに保存
station_df.to_csv('D:\programs\Python\Dokosumi\data\station_list_mesh_minamikanto.tsv', index=False, sep='\t')
