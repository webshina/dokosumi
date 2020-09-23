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

class CollectCntAtStaion:
    def __init__(self):
        sample = ''

    def collectCntAtStaion(self,keyword):
        # 検索対象は中心から1.5km圏内
        radius = 1500

        # 駅名のTSVリストを取得
        tsv_file = 'D:\programs\Python\Dokosumi\data\station_list_kanto.tsv'
        df = pd.read_table(tsv_file)

        #DataFrameに列を追加
        df[keyword] = ''
        print(df)

        s = searchPointsByKeyword.SearchPointsByKeyword()

        # 駅名の数だけ検索
        for row in df.itertuples():

            #検索対象の街を表示
            print(row.station_name)

            latitude = row.lat
            longitude = row.lon
            
            json_txt = s.searchPointsByKeyword(latitude,longitude,radius,keyword)
            print('RESULT:' + str(json_txt))

            cnt = len(json_txt)

            df.at[row.Index, keyword] = cnt

        print('DATAFLAME : ')
        print(df)

        #結果をTSVファイルに保存
        dirname = os.path.dirname(tsv_file)
        filename = os.path.basename(tsv_file)
        df.to_csv(dirname + '\station_list_' + keyword + '.tsv', index=False, sep='\t')

        return 0
