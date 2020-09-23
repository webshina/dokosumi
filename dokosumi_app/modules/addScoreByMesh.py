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

# 駅名のTSVリストを取得
station_tsv_file = 'D:\programs\Python\Dokosumi\data\station_list_mesh.tsv'
station_df = pd.read_table(station_tsv_file)
print(station_df)

# メッシュのCSVリストを取得
theme = 'population'
mesh_csv_file = 'D:\programs\Python\Dokosumi\data\\' + theme + '_kanto.csv'
mesh_df = pd.read_csv(mesh_csv_file)
print(mesh_df)

#駅名DataFrameに列を追加
station_df['SCORE'] = ''

# 駅名の数だけ検索
for row_s in station_df.itertuples():

    #検索対象の街を表示
    print("スコア取得開始：" + row_s.station_name)
    mesh_codes_s = row_s.MESH_CODES
    mesh_codes_s = [ x.strip('[] ') for x in mesh_codes_s.split(',') ]
    
    # 駅のMESH_CODEが統計情報のKEY_CODEに一致する場合、駅名DataFrameにSCOREを追加
    score = 0
    cnt = 0
    for row_m in mesh_df.itertuples():
        if str(row_m.KEY_CODE) in mesh_codes_s:
            score += row_m.AMMOUNT
            cnt += 1
            #print('CORRECT SCORE:' + str(score))
    
    station_df.at[row_s.Index, 'SCORE'] = score / cnt
    print('STATION:' + row_s.station_name + ' SCORE:' + str(score / cnt))

print('DATAFLAME : ')
print(station_df)

#結果をTSVファイルに保存
dirname = os.path.dirname(station_tsv_file)
filename = os.path.basename(station_tsv_file)
station_df.to_csv(dirname + '\station_score_' + theme + '.tsv', index=False, sep='\t')

