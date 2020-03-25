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
xml_list = glob.glob('D:\programs\Python\Dokosumi\data\都市公園\P**\P*.xml', recursive=True)
print(xml_list)

df_all = pd.DataFrame(columns=['ID','LATLON','SCORE'])

for xml_file in xml_list:

    print('XML_FILE:' + xml_file)

    # XMLファイルを解析
    tree = ET.parse(xml_file) 

    # XMLを取得
    root = tree.getroot()

    # gml:Point以下を取得
    pointNodes = root.findall('gml:Point', ns)

    # 座標DataFrameを作成
    df_pos = pd.DataFrame(columns=['ID','LATLON'])

    # DataFrameにid,座標を追加
    for itemNode in pointNodes:
        # idを取得
        id = itemNode.attrib['{' + ns['gml'] + '}' + "id"]

        # 座標を取得
        if itemNode.find('gml:pos', ns) is not None:
            latlon = itemNode.find('gml:pos', ns).text.strip()
        elif itemNode.find('gml:position', ns) is not None:
            latlon = itemNode.find('gml:position', ns).text.strip()

        # DataFrameにid,座標を追加
        df_pos_se = pd.Series([id, latlon], index=df_pos.columns)
        df_pos = df_pos.append(df_pos_se, ignore_index=True)


    # # ksj:LandPrice以下を取得
    pointNodes = root.findall('ksj:Park', ns)

    # SCORE DataFrameを作成
    df_score = pd.DataFrame(columns=['ID','SCORE'])

    # DataFrameにid,SCOREを追加
    for itemNode in pointNodes:

        # idを取得
        if itemNode.find('ksj:loc', ns) is not None:
            id = itemNode.find('ksj:loc', ns).attrib['{' + ns['xlink'] + '}' + "href"].replace('#','')
            # SCOREを取得
            if itemNode.find('ksj:opa', ns).text is not None:
                score = itemNode.find('ksj:opa', ns).text.strip()
            else:
                score = 0
            
        elif itemNode.find('ksj:pos', ns) is not None:
            id = itemNode.find('ksj:pos', ns).attrib['{' + ns['xlink'] + '}' + "href"].replace('#','')
            # SCOREを取得
            score = itemNode.find('ksj:plp', ns).text.strip()
            

        # DataFrameにid,座標を追加
        df_score_se = pd.Series([id, score], index=df_score.columns)
        df_score = df_score.append(df_score_se, ignore_index=True)

    df = pd.merge(df_pos, df_score, on='ID')
    df_all = pd.concat([df_all, df], axis=0, join='inner')

print(df_all)
#結果をTSVファイルに保存
df_all.to_csv('D:\programs\Python\Dokosumi\data\score_by_latlon.tsv', index=False, sep='\t')